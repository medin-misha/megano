from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title')
    freeDelivery = filters.BooleanFilter(field_name='freeDelivery')
    available = filters.BooleanFilter(field_name='available')