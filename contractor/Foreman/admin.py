from django.contrib import admin

from contractor.Foreman.models import FoundationJob, StructureJob

admin.site.register( FoundationJob )
admin.site.register( StructureJob )
