import datetime
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db.models import Q

from .models import CapeTownSlots
from .forms import DaySlotsForm

def stageQuery(stage,area_code):
    """Function to create DB query for stages 1-8 of loadshedding i.e. for stage 6 load-shedding will occur if area code appears as 
    the field value for column stage6 all the way down to column stage1"""

    if stage <1 or stage > 8:
        return 

    stage_query = Q(stage1 = area_code)

    if stage > 1:
        stage_query |= Q(stage2 =area_code)
    if stage > 2:
        stage_query |= Q(stage3 =area_code)
    if stage > 3:
        stage_query |= Q(stage4 =area_code)
    if stage > 4:
        stage_query |= Q(stage5 =area_code)
    if stage > 5:
        stage_query |= Q(stage6 =area_code)
    if stage > 6:
        stage_query |= Q(stage7 =area_code)
    if stage > 7:
        stage_query |= Q(stage8 =area_code)

    if stage > 1:
        stage_query = Q(stage_query)

    return stage_query

def index(request):
    """View function for home page of site."""
    return render(request, 'index.html')

def dayslots(request):
    """Displays load-shedding time slots for a given area based on date and load-shedding stage
        Currently uses cookies but might expand to be user specific"""
    
    s_day = request.session.get('c_day') #Easier to pass day as int instead of extracting from date string
    s_area = request.session.get('c_area')
    s_stage = request.session.get('c_stage')
    s_date = request.session.get('c_date')

    slots_query = Q(day=s_day) &  stageQuery(s_stage,s_area)
    day_slots = CapeTownSlots.objects.filter(slots_query)
    context = {"day_slots": day_slots,
               "date": s_date
               }
    return render(request, "loadshedding_calc/day.html", context)


def selection(request):
    """Simple form to enter relevent details to get load-shedding schedule for a particular day, area and load-shedding stage.
        Uses POST for django builtin security"""
    
    if request.method == 'POST':

        form = DaySlotsForm(request.POST)

        if form.is_valid():
            date = form.cleaned_data['selected_date']
            area = form.cleaned_data['selected_area']
            stage = form.cleaned_data['selected_stage']
            
            request.session['c_day'] = date.day
            request.session['c_date'] = date.strftime("%A %d %B %Y")
            request.session['c_area'] = area
            request.session['c_stage'] = stage

            return HttpResponseRedirect(reverse('day-slots'))

    else:
        form = DaySlotsForm(request.POST)

    context = {
        'form': form,
    }

    return render(request, 'loadshedding_calc/selection.html', context)
  
