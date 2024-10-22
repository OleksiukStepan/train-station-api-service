from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "latitude", "longitude"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

    def validate(self, attrs: dict) -> dict:
        source = attrs.get("source", getattr(self.instance, "source", None))
        destination = attrs.get(
            "destination", getattr(self.instance, "destination", None)
        )

        if source == destination:
            raise serializers.ValidationError(
                "Source and destination can't be the same"
            )

        return super().validate(attrs)


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
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ["id", "name"]


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "image"]


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type"]


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )

    class Meta(TrainSerializer.Meta):
        model = Train
        fields = TrainSerializer.Meta.fields + ["image"]


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer()

    class Meta(TrainSerializer.Meta):
        model = Train
        fields = TrainSerializer.Meta.fields + ["image"]


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "image"]


class CrewSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "image"]


class JourneySerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",)
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = [
            "id",
            "route",
            "train",
            "tickets_available",
            "crew",
            "departure_time",
            "arrival_time"
        ]

    def validate(self, attrs: dict) -> dict:
        if attrs["departure_time"] >= attrs["arrival_time"]:
            raise serializers.ValidationError(
                "Departure time cannot be later than or equal to arrival time"
            )

        return super().validate(attrs)


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
            f"{first_name} {last_name}"
            for first_name, last_name in obj.crew.values_list(
                "first_name", "last_name"
            )
        ]


class JourneyDetailSerializer(JourneySerializer):  #
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey"]

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(read_only=True)


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyDetailSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%d %H:%M:%S",
    )
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "tickets", "created_at"]

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
