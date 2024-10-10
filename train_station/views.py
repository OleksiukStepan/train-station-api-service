from rest_framework import viewsets

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
from train_station.serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderSerializer,
    OrderDetailSerializer,
    TrainSerializer,
    TrainTypeSerializer,
    CrewSerializer,
    JourneySerializer,
    TicketSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related("route", "train")
        .prefetch_related("crew")
    )
    serializer_class = JourneySerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("journey", "order")
    serializer_class = TicketSerializer
