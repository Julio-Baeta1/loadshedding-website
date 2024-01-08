from django_filters import rest_framework as filters
from .models import CapeTownPastStages

class CTPastStagesDateFilterSet(filters.FilterSet):
    min_date = filters.DateFilter(field_name="date", lookup_expr='gte')
    max_date = filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = CapeTownPastStages
        fields = ['stage'] #Fill with optional fields like filterset_fields in view for equality