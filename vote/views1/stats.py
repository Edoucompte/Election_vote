from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response, status
from rest_framework.views import APIView

from vote.models import Candidate, CustomUser, Election, Vote
from vote.views1.user import CustomAuthentication, res


def _get_org_election(pk, organisation):
    # Org-scoped lookup, same pattern as the other views: no leak of
    # cross-org election existence.
    return Election.objects.filter(pk=pk, organisation=organisation).first()


def _vote_breakdown(election):
    """Per-candidate vote counts/percentages for an election, sorted desc."""
    accepted = Candidate.objects.filter(election=election, status='accepte').select_related('candidate')
    vote_counts = {
        row['candidate_id']: row['n']
        for row in Vote.objects.filter(election=election).values('candidate_id').annotate(n=Count('id'))
    }
    total_votes = sum(vote_counts.values())
    rows = []
    for c in accepted:
        votes = vote_counts.get(c.candidate_id, 0)
        rows.append({
            "candidate_id": c.candidate_id,
            "candidate_name": f"{c.candidate.first_name} {c.candidate.last_name}".strip(),
            "votes": votes,
            "percentage": round(votes / total_votes * 100, 2) if total_votes else 0,
        })
    rows.sort(key=lambda r: r["votes"], reverse=True)
    return rows, total_votes


class ElectionResultsView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Vote results for one election", responses=res)
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        election = _get_org_election(pk, request.user.organisation)
        if election is None:
            return response.Response({"succes": False, "errors": "Élection introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Electors only see results once the election is over; supervisors can watch live.
        if not request.user.is_supervisor and timezone.now() < election.end_date:
            return response.Response({
                "succes": False,
                "errors": "Les résultats ne sont disponibles qu'à la clôture de l'élection."
            }, status=status.HTTP_403_FORBIDDEN)

        rows, total_votes = _vote_breakdown(election)
        winner = rows[0] if rows and rows[0]["votes"] > 0 else None

        return response.Response({
            "succes": True,
            "details": "Résultats de l'élection",
            "data": {
                "election_id": election.id,
                "total_votes": total_votes,
                "results": rows,
                "winner": winner,
            }
        }, status=status.HTTP_200_OK)


class ElectionStatsView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Turnout stats for one election", responses=res)
    def get(self, request, pk):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        election = _get_org_election(pk, request.user.organisation)
        if election is None:
            return response.Response({"succes": False, "errors": "Élection introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # No per-election voter roster in the data model: eligibility is
        # "every elector of the organisation".
        inscrits = CustomUser.objects.filter(organisation=election.organisation, is_elector=True).count()
        votants = Vote.objects.filter(election=election).values('elector_id').distinct().count()
        participation = round(votants / inscrits * 100, 2) if inscrits else 0

        rows, _ = _vote_breakdown(election)
        if len(rows) >= 2:
            marge = round(rows[0]["percentage"] - rows[1]["percentage"], 2)
        else:
            marge = rows[0]["percentage"] if rows else 0

        return response.Response({
            "succes": True,
            "details": "Statistiques de l'élection",
            "data": {
                "inscrits": inscrits,
                "votants": votants,
                "participation": participation,
                "marge": marge,
                "resultats": rows,
            }
        }, status=status.HTTP_200_OK)


class OrganisationStatsView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Supervisor dashboard aggregates for the connected org", responses=res)
    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        org = request.user.organisation
        now = timezone.now()
        elections = Election.objects.filter(organisation=org)
        candidatures = Candidate.objects.filter(election__organisation=org)
        total_inscrits = CustomUser.objects.filter(organisation=org, is_elector=True).count()

        # Average turnout across ended elections only (ongoing ones would skew it low).
        ended = elections.filter(end_date__lt=now)
        rates = []
        if total_inscrits:
            for election in ended:
                votants = Vote.objects.filter(election=election).values('elector_id').distinct().count()
                rates.append(votants / total_inscrits * 100)
        taux_moyen = round(sum(rates) / len(rates), 2) if rates else 0

        return response.Response({
            "succes": True,
            "details": "Statistiques de l'organisation",
            "data": {
                "totalElections": elections.count(),
                "activeElections": elections.filter(begin_date__lte=now, end_date__gte=now).count(),
                "pendingCandidatures": candidatures.filter(status='en_attente').count(),
                "activeCandidates": candidatures.filter(status='accepte').count(),
                "totalInscrits": total_inscrits,
                "tauxParticipation": taux_moyen,
            }
        }, status=status.HTTP_200_OK)


class ElectorStatsView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Elector dashboard aggregates", responses=res)
    def get(self, request):
        if not request.user.is_authenticated:
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        org = request.user.organisation
        now = timezone.now()
        active_elections = Election.objects.filter(organisation=org, begin_date__lte=now, end_date__gte=now)
        pending = Candidate.objects.filter(candidate=request.user, status='en_attente')
        participated = Vote.objects.filter(elector=request.user).values('election_id').distinct().count()

        return response.Response({
            "succes": True,
            "details": "Statistiques de l'électeur",
            "data": {
                "activeElections": active_elections.count(),
                "pendingCandidatures": pending.count(),
                "participatedElections": participated,
            }
        }, status=status.HTTP_200_OK)


class SendElectionResultsView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Email election results to the org's electors", responses=res)
    def post(self, request, pk):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        election = _get_org_election(pk, request.user.organisation)
        if election is None:
            return response.Response({"succes": False, "errors": "Élection introuvable."}, status=status.HTTP_404_NOT_FOUND)

        rows, total_votes = _vote_breakdown(election)
        winner = rows[0] if rows and rows[0]["votes"] > 0 else None
        lines = "\n".join(f"- {r['candidate_name']}: {r['votes']} voix ({r['percentage']}%)" for r in rows)
        body = (
            f"Résultats de l'élection \"{election.name}\" :\n\n{lines}\n\n"
            f"Vainqueur : {winner['candidate_name'] if winner else 'Aucun'}\n"
            f"Total des votes exprimés : {total_votes}"
        )

        recipients = list(
            CustomUser.objects.filter(organisation=election.organisation, is_elector=True)
            .exclude(email='').values_list('email', flat=True)
        )
        sent, failed = 0, 0
        for email in recipients:
            try:
                send_mail(f"Résultats : {election.name}", body, 'super@vote.com', [email], fail_silently=False)
                sent += 1
            except Exception:
                failed += 1

        return response.Response({
            "succes": True,
            "details": f"Résultats envoyés à {sent} électeur(s)" + (f", {failed} échec(s)" if failed else ""),
        }, status=status.HTTP_200_OK)
