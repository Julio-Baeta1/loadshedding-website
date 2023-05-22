import datetime
from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class DaySlotsForm(forms.Form):
    selected_date = forms.DateField(help_text="Enter date in form dd/mm/yyyy",input_formats=['%d/%m/%Y'])
    selected_area = forms.IntegerField(help_text="Enter your area code")
    selected_stage = forms.IntegerField(help_text="Enter the loadshedding stage")


    def clean_selected_date(self):
        data_day = self.cleaned_data['selected_date']
        
        #Must add further validation
        if data_day.day < 1 or data_day.day > 31:   
            raise ValidationError(_('Not a valid date'))
        
        return data_day
    
    def clean_selected_area(self):
        data_area = self.cleaned_data['selected_area']

        if data_area < 1 or data_area > 16:
            raise ValidationError(_('Not a valid area code'))
        
        return data_area
    
    def clean_selected_stage(self):
        data_stage = self.cleaned_data['selected_stage']

        if data_stage < 1 or data_stage > 8:
            raise ValidationError(_('Not a valid loadshedding stage'))
        
        return data_stage