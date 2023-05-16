from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db.models import Q

from .models import CapeTownSlots, TimeSlot
from .forms import DaySlotsForm

def stageQuery(stage,area_code):

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

def detail(request, slot_id):
    return HttpResponse("You're looking at %s." % slot_id)


def index(request):
    day_slots = CapeTownSlots.objects.filter(Q(day=1) &  Q(Q(stage1=1) | Q(stage2=1)))
    context = {"day_slots": day_slots}
    return render(request, "loadshedding_calc/index.html", context)

def dayslots(request):
    s_day = request.session.get('c_day')
    s_area = request.session.get('c_area')
    s_stage = request.session.get('c_stage')

    slots_query = Q(day=s_day) &  stageQuery(s_stage,s_area)
    day_slots = CapeTownSlots.objects.filter(slots_query)
    context = {"day_slots": day_slots}
    return render(request, "loadshedding_calc/day.html", context)


def selection(request):
    
    if request.method == 'POST':

        form = DaySlotsForm(request.POST)

        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            #book_instance.due_back = form.cleaned_data['renewal_date']
            #book_instance.save()
            day = form.cleaned_data['selected_day']
            area = form.cleaned_data['selected_area']
            stage = form.cleaned_data['selected_stage']
            #print(area)
            request.session['c_day'] = day
            request.session['c_area'] = area
            request.session['c_stage'] = stage

            return HttpResponseRedirect(reverse('day-slots'))

    else:
        #proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        #form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form = DaySlotsForm(request.POST)

    context = {
        'form': form,
        #'book_instance': book_instance,
    }

    return render(request, 'loadshedding_calc/selection.html', context)

#class IndexView(generic.ListView):
#    template_name = "loadshedding_clac/index.html"
#    context_object_name = "area_code_list"

#    def get_queryset(self):
#        return CapeTownSlots.objects.filter(day=5)
#        #return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

#class ResultsView(generic.DetailView):
#    model = CapeTownSlots
#    template_name = "loads/results.html"    
