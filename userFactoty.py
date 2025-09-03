from vote.models import *

for user in range(40):
    CustomUser.objects.create(
        email = f"user{user}@example.com",
        sexe = 'M' if user % 2 == 0 else 'F',
        date_naissance = '2000-01-01',
        matricule = user,
        is_superviseur=True if user % 2 == 0 else False,
        is_electeur=True,
        is_candidat=False,
        first_name= f"User first name{user}",
        last_name= f"User last name{user}"
    )

#bulck_create()