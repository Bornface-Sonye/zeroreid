from django.contrib import admin

from . models import Case, County, Constituency,Ward,Location,Sub_Location,Police_Officer,Police_Station,Response,Suspect,Badge_Number

models_to_register = [Case, County, Constituency,Ward,Location,Sub_Location,Police_Officer,Police_Station,Response,Suspect,Badge_Number]

for model in models_to_register:
    admin.site.register(model)
