from django.contrib import admin
from .models import Company, Door
from .forms import AllowedPersonForm


@admin.register(Door)
class DoorAdmin(admin.ModelAdmin):
    form = AllowedPersonForm

    # A template for a customized change view:
    change_form_template = 'admin/company/door/door_change_form.html'

    list_display = ['pk', 'name', 'company_name']
    search_fields = ['name', 'company__company_name']
    list_filter = ['name', 'company__company_name']

    def company_name(self, obj):
        return obj.company.company_name

    class Media:
        js = ('js/jquery-3.3.1.min.js',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company_name', 'timezone']
    search_fields = ['company_name']
    list_filter = ['company_name']
