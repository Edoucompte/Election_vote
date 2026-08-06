from django.contrib import admin

from vote.models import CustomUser, Organisation, Invitation, Plan, Subscription

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Organisation)
admin.site.register(Invitation)
admin.site.register(Plan)
admin.site.register(Subscription)