from django.contrib import admin

from .models import USDCitizenRequest, Petition, VoteU
# Register your models here.

admin.site.register(USDCitizenRequest)
admin.site.register(VoteU)
admin.site.register(Petition)