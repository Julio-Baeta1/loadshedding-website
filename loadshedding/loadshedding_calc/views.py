import datetime
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db.models import Q
from django.db import transaction

from .models import CapeTownSlots, CapeTownPastStages, CapeTownAreas, Profile
from .forms import DaySlotsForm, DaySlotsFormLoggedIn, UserForm, ProfileForm

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

    if stage > 1: #Ensures that if only single query in Q object it is not encapsulated by larger Q()
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

    if s_stage == 0:
        day_slots = CapeTownSlots.objects.none()
    else:
        slots_query = Q(day=s_day) &  stageQuery(s_stage,s_area)
        day_slots = CapeTownSlots.objects.filter(slots_query)

    context = {"day_slots": day_slots,
               "date": s_date
               }
    return render(request, "loadshedding_calc/day.html", context)

def dayslotsLoggedIn(request):
    """Displays load-shedding time slots for a given day based on logged in user's area code"""
     
    u_date = datetime.datetime.strptime(request.session.get('c_date'), "%d-%m-%Y").date()
    u_area = request.user.profile.getUserArea()
    final_obj = CapeTownSlots.objects.none()

    u_start = request.user.profile.getUserStartTime()
    u_end = request.user.profile.getUserEndTime()

    #day_stages gets all load-shedding stage values and time intervals that occur during user's selected day time allocations
    day_stages = CapeTownPastStages.filterDateTimes(CapeTownPastStages ,u_date,u_start,u_end)

    #final_obj contains all slots that user will experience loadshedding for their allocated day time hours
    for obj in day_stages:
        temp_obj = CapeTownSlots.filterbyStageTimes(CapeTownSlots, u_date.day,u_area,obj.stage,u_start,u_end)
        final_obj = final_obj | temp_obj

    context = {"day_slots": final_obj,
               "date": u_date.strftime("%A %d %B %Y")
               }
    return render(request, "loadshedding_calc/day.html", context)


def selection(request):
    """Simple form to enter relevent details to get load-shedding schedule for a particular day, area and load-shedding stage.
        Uses POST for django builtin security"""
    if request.user.is_authenticated:
            #Logged in User form
            if request.method == 'POST':

                form = DaySlotsFormLoggedIn(request.POST)

                if form.is_valid():
                    date = form.cleaned_data['selected_date']
            
                request.session['c_date'] = date.strftime("%d-%m-%Y")

                return HttpResponseRedirect(reverse('day-slots-logged-in'))

            else:
                form = DaySlotsFormLoggedIn(request.POST)

            context = {
                'form': form,
            }

            return render(request, 'loadshedding_calc/selection.html', context)

    else:
        #Anonymous web user form
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

class UserProfileView(LoginRequiredMixin,generic.DetailView):
    """Generic class-based view for user profile."""
    template_name = 'loadshedding_calc/user_profile.html'

    def get_object(self):
        return self.request.user

@login_required
@transaction.atomic
def edit_profile(request):

    if request.method == 'POST':

        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('user-profile'))
        
    else:

        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'loadshedding_calc/edit_profile.html', context)




    