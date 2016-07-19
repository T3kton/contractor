from django.contrib import admin

from contractor.Building.models import Foundation, Structure, Complex

admin.site.register( Foundation )
admin.site.register( Structure )
admin.site.register( Complex )
