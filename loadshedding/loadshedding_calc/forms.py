import datetime
from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, Profile, CapeTownPastStages

class TimePickerInput(forms.TimeInput):
        input_type = 'time'

class DatePickerInput(forms.DateInput):
        input_type = 'date'

class DaySlotsForm(forms.Form):
    #error_css_class = "error"
    selected_date = forms.DateField(widget=DatePickerInput)
    selected_area = forms.IntegerField(label="Enter your area code")

    widgets = {
            'selected_area': forms.NumberInput(attrs={'min': "1", 'max': "16", 'step': "1", 'default': "1"}),
    }

    def clean_selected_date(self):
        data_day = self.cleaned_data['selected_date']
        
        #Must add further validation
        #if data_day.day < 1 or data_day.day > 31:   
        #    raise ValidationError(_('Not a valid date'))
        if data_day < CapeTownPastStages.getEarliestDate(CapeTownPastStages) or data_day > CapeTownPastStages.getLatestDate(CapeTownPastStages):
            raise ValidationError(_('No load-shedding stage information avaliable for selected date'))

        return data_day
    
    def clean_selected_area(self):
        data_area = self.cleaned_data['selected_area']

        if data_area < 1 or data_area > 16:
            raise ValidationError(_('Not a valid area code'))
        
        return data_area
    
    
class DaySlotsFormLoggedIn(forms.Form):
    
    selected_date = forms.DateField(widget=DatePickerInput)

    def clean_selected_date(self):
        data_day = self.cleaned_data['selected_date']
        
        #Must add further validation
        if data_day.day < 1 or data_day.day > 31:   
            raise ValidationError(_('Not a valid date'))
        
        return data_day
    

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user_area', 'user_hour_cost', 'user_time_start', 'user_time_end')
        widgets = {
            'user_hour_cost': forms.NumberInput(attrs={'min': "0.00", 'max': "10000.00", 'step': "0.01"}),
            'user_time_start': TimePickerInput(format='%H:%M'),
            'user_time_end': TimePickerInput(format='%H:%M')
        }
        labels = {
            'user_area': "Select your Cape Town area",
            'user_hour_cost': "Set your cost per hour (R)",
            'user_time_start': "Set your usage window start time for the day",
            'user_time_end': "Set your usage window end time for the day"
        }