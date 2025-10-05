from django.contrib import admin
from .models import Fonctionnalite
from .models import Antecedent
from .models import Prescription


admin.site.register(Prescription)

admin.site.register(Antecedent)



# Register your models here.

@admin.register(Fonctionnalite)
class FonctionnaliteAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'statut')
    list_filter = ('statut',)
    search_fields = ('nom', 'code')

    