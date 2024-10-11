from datetime import datetime

import django_filters
from django.db.models import QuerySet


class RouteFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(
        field_name="source__name",
        lookup_expr="icontains"
    )
    destination = django_filters.CharFilter(
        field_name="destination__name",
        lookup_expr="icontains"
    )


class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.CharFilter(method="filter_created_at")

    def filter_created_at(
            self,
            queryset: QuerySet,
            name: str,
            value: str
    ) -> QuerySet:
        try:
            date = datetime.strptime(value, "%Y-%m-%d").date()
            return queryset.filter(created_at__date=date)
        except ValueError:
            return queryset


class TrainFilter(django_filters.FilterSet):
    train_type = django_filters.CharFilter(method="filter_train_type")

    def filter_train_type(
            self,
            queryset: QuerySet,
            name: str,
            value: str
    ) -> QuerySet:
        try:
            train_type_ids = [int(pk) for pk in value.split(",")]
            return queryset.filter(train_type__id__in=train_type_ids)
        except ValueError:
            return queryset


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
