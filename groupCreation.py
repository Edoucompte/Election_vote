from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from vote.models import Vote, Candidate

# get or create Elctor group
elector_group, created =Group.objects.get_or_create(name="Elector")
print("Groupe election new creation : ", created)


# recuperer les permissions de electeurs et les assigner au group
# voir elections
view_election_perm = Permission.objects.get(codename="view_election")
elector_group.permissions.add(view_election_perm)

# voir-qjouter-modifier-supprimer votes
vote_content_type = ContentType.objects.get_for_model(Vote)
# list des permissions de vote add-view-change-delete
vote_permissions = Permission.objects.filter(content_type=vote_content_type) 
[elector_group.permissions.add(perm) for perm in vote_permissions]

#poser, voir ou suppriner sa candidature
candidate_content_type = ContentType.objects.get_for_model(Candidate)
# list des permissions de vote add-view-change-delete
candidate_permissions = Permission.objects.filter(content_type=candidate_content_type) 
[elector_group.permissions.add(perm) for perm in candidate_permissions if not perm.codename == 'change_candidate']

'''
    User peut :
    - poser sa candidature, 
    - voir, modifier ou supprimer ses candidatures uniquement
    
    - voir les candidats, (candidatures acceptees par superviseur) par election
'''

