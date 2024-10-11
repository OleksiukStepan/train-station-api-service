from django.db.models import QuerySet
from rest_framework import viewsets

from train_station.filters import (
    RouteFilter,
    OrderFilter,
    TrainFilter,
    JourneyFilter,
)
from train_station.models import (
    Station,
    Route,
    Order,
    Train,
    TrainType,
    Crew,
    Journey,
    Ticket,
)
from train_station.ordering import OrderingHelper
from train_station.serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    CrewSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["name"]
        )
        return queryset.order_by(*ordering_fields)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["name"]
        )
        return queryset.order_by(*ordering_fields)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    filterset_class = RouteFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user")
    filterset_class = OrderFilter

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    filterset_class = TrainFilter

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related("route", "train")
        .prefetch_related("crew")
    )
    filterset_class = JourneyFilter

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("journey", "order")

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer
