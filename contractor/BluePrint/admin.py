from django.contrib import admin

from contractor.BluePrint.models import FoundationBluePrint, StructureBluePrint, Script, BluePrintScript

admin.site.register( FoundationBluePrint )
admin.site.register( StructureBluePrint )
admin.site.register( Script )
admin.site.register( BluePrintScript )
