from vote.models import *

for user in range(40):
    CustomUser.objects.create(
        email= f"user{user}@example.com",
        sex= 'M' if user % 2 == 0 else 'F',
        birth_date = '2000-01-01',
        matricule= user,
        is_supervisor=True if user % 2 == 0 else False,
        is_elector= True,
        is_candidate= False,
        first_name= f"User first name{user}",
        last_name= f"User last name{user}"
    )

#bulck_create()