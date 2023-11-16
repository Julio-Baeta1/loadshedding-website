from rest_framework import serializers 
from loadshedding_calc.models import CapeTownPastStages, CapeTownAreas
  
class CapeTownPastStagesSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CapeTownPastStages
        fields = ['date','stage','start_time','end_time']

class AreaSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = CapeTownAreas
        fields = ['area_name','area_code']