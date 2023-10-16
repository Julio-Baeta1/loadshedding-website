import datetime

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db import transaction

from .models import CapeTownSlots, CapeTownPastStages, CapeTownAreas, Profile, oneDaySlotsBetweenTimes
from .forms import DaySlotsForm, DaySlotsFormLoggedIn, UserForm, ProfileForm

def home(request):
    """View function for home page of site."""
    return render(request, 'home.html')

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
                    date = form.clean_selected_date()           
                    url_date = date.strftime("%d-%m-%Y")

                    return HttpResponseRedirect(reverse("day-slots-logged-in",args=[request.user.username])+f"?date={url_date}")

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
                date = form.clean_selected_date()
                area = form.clean_selected_area()

                url_date = date.strftime("%d-%m-%Y")
                url_area = area

                return HttpResponseRedirect(reverse('day-slots')+f"?area_code={url_area}&date={url_date}")

        else:
            form = DaySlotsForm(request.POST)

        context = {
            'form': form,
        }

        return render(request, 'loadshedding_calc/selection.html', context)

###################################################################################################################################
#Anonymous web user slots for day view

def dayslots(request):
    """Displays load-shedding time slots for a given area based on date and load-shedding stage
        Currently uses cookies but might expand to be user specific"""
    
    area = request.GET.get('area_code')
    date = request.GET.get('date')

    #################
    #Since uses url an extra layer of testing is required
    #Test area code is valid
    if area is None:
        return render(request, "loadshedding_calc/invalid_day.html")
    try:
        area = int(area)
    except ValueError:
        return render(request, "loadshedding_calc/invalid_day.html")    
    if area < 1 or area > 16:
        return render(request, "loadshedding_calc/invalid_day.html")
    
    #Test date is valid 
    if date is None:
        return render(request, "loadshedding_calc/invalid_day.html") 
    try:
        date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    except ValueError:
        return render(request, "loadshedding_calc/invalid_day.html")
    if date < CapeTownPastStages.getEarliestDate(CapeTownPastStages) or date > CapeTownPastStages.getLatestDate(CapeTownPastStages):   
        return render(request, "loadshedding_calc/invalid_day.html")
    #################

    #Get query set
    final_obj = oneDaySlotsBetweenTimes(date,area,datetime.time(0,0),datetime.time(23,59))

    context = {
                "day_slots": final_obj,
                "date": date.strftime("%A %d %B %Y")
              }

    return render(request, "loadshedding_calc/day.html", context)


###################################################################################################################################
#Logged in web user slots for day view

#def dayslotsLoggedIn(request):
@login_required
def dayslotsLoggedIn(request,username):
    """Displays load-shedding time slots for a given day based on logged in user's area code"""
     
    date = request.GET.get('date')

    #################
    #Since uses url an extra layer of testing is required
    #Test date is valid 
    if date is None:
        return render(request, "loadshedding_calc/invalid_day.html") 
    try:
        date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    except ValueError:
        return render(request, "loadshedding_calc/invalid_day.html")
    if date < CapeTownPastStages.getEarliestDate(CapeTownPastStages) or date > CapeTownPastStages.getLatestDate(CapeTownPastStages):   
        return render(request, "loadshedding_calc/invalid_day.html")
    #################

    area = request.user.profile.getUserArea()
    start = request.user.profile.getUserStartTime()
    end = request.user.profile.getUserEndTime()
    
    final_obj = oneDaySlotsBetweenTimes(date,area,start,end)

    context = {
                "day_slots": final_obj,
                "date": date.strftime("%A %d %B %Y")
              }
    
    return render(request, "loadshedding_calc/day.html", context)
    
###################################################################################################################################
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




    