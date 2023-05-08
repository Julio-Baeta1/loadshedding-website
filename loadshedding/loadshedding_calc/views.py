from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from django.db.models import Q

from .models import CapeTownSlots

def detail(request, slot_id):
    return HttpResponse("You're looking at %s." % slot_id)


def index(request):
    day_slots = CapeTownSlots.objects.filter(Q(day=1) &  Q(Q(stage1=1) | Q(stage2=1)))
    context = {"day_slots": day_slots}
    return render(request, "loadshedding_calc/index.html", context)

#def selection(request):


#class IndexView(generic.ListView):
#    template_name = "loadshedding_clac/index.html"
#    context_object_name = "area_code_list"

#    def get_queryset(self):
#        return CapeTownSlots.objects.filter(day=5)
#        #return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

#class ResultsView(generic.DetailView):
#    model = CapeTownSlots
#    template_name = "loads/results.html"    
