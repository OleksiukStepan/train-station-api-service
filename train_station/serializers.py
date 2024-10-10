from django.utils import timezone
from rest_framework import serializers

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
from user.models import User
from user.serializers import UserSerializer


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "latitude", "longitude"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]

    def get_created_at(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")


class OrderListSerializer(OrderSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="email",
    )


class OrderDetailSerializer(OrderSerializer):
    user = UserSerializer(many=False, read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ["id", "name"]


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type"]


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=False)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class JourneySerializer(serializers.ModelSerializer):
    departure_time = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = [
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time"
        ]

    def get_departure_time(self, obj) -> str:
        return (
            timezone.localtime(obj.departure_time)
            .strftime("%Y-%m-%d %H:%M:%S")
        )

    def get_arrival_time(self, obj) -> str:
        return (
            timezone.localtime(obj.arrival_time).strftime("%Y-%m-%d %H:%M:%S")
        )


class JourneyListSerializer(JourneySerializer):  #
    route = serializers.SerializerMethodField()
    train = serializers.CharField(
        source="train.train_type.name",
        read_only=True
    )
    crew = serializers.SerializerMethodField()

    def get_route(self, obj: Journey) -> str:
        return f"{obj.route.source.name} -> {obj.route.destination.name}"

    def get_crew(self, obj: Journey) -> list[str]:
        return [
            f"{person.first_name} {person.last_name}"
            for person in obj.crew.all()
        ]


class JourneyDetailSerializer(JourneySerializer):  #
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteListSerializer(many=False, read_only=True)
    train = TrainListSerializer(many=False, read_only=True)
    departure_time = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey", "order"]
