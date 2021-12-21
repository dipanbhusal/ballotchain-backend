from django.contrib import admin
from . import models 
# Register your models here.
admin.site.register(models.Users)
admin.site.register(models.RSAKeys)

admin.site.site_header = 'BallotChain'
admin.site.index_title = 'Admin Panel For BallotChain'
