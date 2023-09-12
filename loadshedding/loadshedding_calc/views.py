import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db import transaction

from .models import CapeTownSlots, CapeTownPastStages, CapeTownAreas, Profile
from .forms import DaySlotsForm, DaySlotsFormLoggedIn, UserForm, ProfileForm

def index(request):
    """View function for home page of site."""
    return render(request, 'index.html')

###################################################################################################################################
#Day Slot Selection Views

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

                request.session['c_date'] = date.strftime("%d-%m-%Y")
                request.session['c_area'] = area

                return HttpResponseRedirect(reverse('day-slots'))

        else:
            form = DaySlotsForm(request.POST)

        context = {
            'form': form,
        }

        return render(request, 'loadshedding_calc/selection.html', context)

#Anonymous web user slots for day view
def dayslots(request):
    """Displays load-shedding time slots for a given area based on date and load-shedding stage
        Currently uses cookies but might expand to be user specific"""
    
    s_area = request.session.get('c_area')
    s_date = datetime.datetime.strptime(request.session.get('c_date'), "%d-%m-%Y").date()

    s_start = datetime.time(0,0)
    s_end = datetime.time(23,59)
    final_obj = CapeTownSlots.objects.none()

    #day_stages gets all load-shedding stage values and time intervals that occur during user's selected day time allocations
    day_stages = CapeTownPastStages.filterDateTimes(CapeTownPastStages ,s_date,s_start,s_end)

    #final_obj contains all slots that user will experience loadshedding for their allocated day time hours
    for obj in day_stages:
        temp_obj = CapeTownSlots.filterbyStageTimes(CapeTownSlots, s_date.day,s_area,obj.stage,s_start,s_end)
        final_obj = final_obj | temp_obj

    context = {"day_slots": final_obj,
               "date": s_date.strftime("%A %d %B %Y")
               }

    return render(request, "loadshedding_calc/day.html", context)

#Logged in web user slots for day view
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
    
###################################################################################################################################
#User profile views

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




    