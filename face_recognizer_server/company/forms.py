from django import forms
from stuff.models import Person
from .models import Door


class AllowedPersonForm(forms.ModelForm):
    class Meta:
        model = Door
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AllowedPersonForm, self).__init__(*args, **kwargs)
        try:
            company_pk = self.initial['company']
            self.fields['allowed_person'].queryset = Person.active_objects.filter(company=company_pk)
        except KeyError:
            self.fields['allowed_person'].queryset = Person.active_objects.filter(company=None)
