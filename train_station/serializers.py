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
    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]


class OrderListSerializer(OrderSerializer):
    created_at = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="email",
    )

    def get_created_at(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")


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


class JourneySerializer(serializers.ModelSerializer):  #
    crew = CrewSerializer(many=True, read_only=True)

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


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey", "order"]
