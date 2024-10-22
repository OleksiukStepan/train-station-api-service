from typing import Type

from django.db.models import QuerySet, F, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

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
    stations,
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
    CrewImageSerializer,
    TrainImageSerializer,
)


class UploadImageMixin:
    image_serializer_class = None

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request: Request, pk: int = None) -> Response:
        if "image" not in request.data:
            return Response(
                {"detail": "No image provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = self.get_object()
        serializer = self.image_serializer_class(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@stations.station_schema
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["name"]
        )
        return queryset.order_by(*ordering_fields)


@train_types.train_type_schema
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["name"]
        )
        return queryset.order_by(*ordering_fields)


@crews.crew_schema
class CrewViewSet(viewsets.ModelViewSet, UploadImageMixin):
    queryset = Crew.objects.all()
    image_serializer_class = CrewImageSerializer

    def get_serializer_class(self):
        if self.action == "upload_image":
            return TrainImageSerializer

        return CrewSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
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
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


@orders.order_schema
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user")
    filterset_class = OrderFilter

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset().filter(user=self.request.user)
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=["created_at"]
        )
        return queryset.order_by(*ordering_fields)

    def perform_create(self, serializer: OrderSerializer) -> None:
        serializer.save(user=self.request.user)


@trains.train_schema
class TrainViewSet(viewsets.ModelViewSet, UploadImageMixin):
    queryset = Train.objects.select_related("train_type")
    filterset_class = TrainFilter
    image_serializer_class = TrainImageSerializer
    ordering_fields = ["name", "cargo_num", "places_in_cargo", "train_type"]

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainDetailSerializer
        elif self.action == "upload_image":
            return TrainImageSerializer

        return TrainSerializer


@journeys.journey_schema
class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related("route", "train")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets")
            )
        )
    )
    filterset_class = JourneyFilter
    ordering_fields = ["route", "train", "departure_time", "arrival_time"]

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


@tickets.ticket_schema
class TicketViewSet(viewsets.ModelViewSet):
    queryset = (
        Ticket.objects.select_related("journey", "order")
        .prefetch_related("journey__crew")
    )
    ordering_fields = ["cargo", "seat", "journey"]

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        ordering_fields = OrderingHelper.get_ordering_fields(
            self.request, fields=self.ordering_fields
        )
        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketDetailSerializer

        return TicketSerializer
