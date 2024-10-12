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
from train_station.schemas import (
    routes,
    orders,
    trains,
    journeys,
    tickets,
    crews,
    train_types,
)
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


@train_types.train_type_schema
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["name"]
        )
        return queryset.order_by(*ordering_fields)


@crews.crew_schema
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["first_name", "last_name"]
        )
        return queryset.order_by(*ordering_fields)


@routes.route_schema
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    filterset_class = RouteFilter
    ordering_fields = ["source", "destination", "distance"]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


@orders.order_schema
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
        queryset = self.queryset    #.filter(user=self.request.user)
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["created_at"]
        )
        return queryset.order_by(*ordering_fields)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@trains.train_schema
class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    filterset_class = TrainFilter
    ordering_fields = ["name", "cargo_num", "places_in_cargo", "train_type"]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer

@journeys.journey_schema
class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related("route", "train")
        .prefetch_related("crew")
    )
    filterset_class = JourneyFilter
    ordering_fields = ["route", "train", "departure_time", "arrival_time"]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


@tickets.ticket_schema
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("journey", "order")
    ordering_fields = ["cargo", "seat", "journey"]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer
