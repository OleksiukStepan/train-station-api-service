from datetime import datetime

import django_filters
from django.db.models import QuerySet


class JourneyFilter(django_filters.FilterSet):
    departure_time = django_filters.CharFilter(method="filter_departure_time")
    arrival_time = django_filters.CharFilter(method="filter_arrival_time")
    source = django_filters.CharFilter(
        field_name="route__source__name",
        lookup_expr="icontains",
    )
    destination = django_filters.CharFilter(
        field_name="route__destination__name",
        lookup_expr="icontains"
    )

    def filter_departure_time(
            self,
            queryset: QuerySet,
            name: str,
            value: str
    ) -> QuerySet:
        try:
            date = datetime.strptime(value, "%Y-%m-%d").date()
            return queryset.filter(departure_time__date=date)
        except ValueError:
            return queryset

    def filter_arrival_time(
            self,
            queryset: QuerySet,
            name: str,
            value: str
    ) -> QuerySet:
        try:
            date = datetime.strptime(value, "%Y-%m-%d").date()
            return queryset.filter(arrival_time__date=date)
        except ValueError:
            return queryset
