import os
import uuid
from typing import Type, Union

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from train_station_core import settings


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ["latitude", "longitude"]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, related_name="routes_from", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station, related_name="routes_to", on_delete=models.CASCADE
    )
    distance = models.PositiveIntegerField()

    class Meta:
        unique_together = ["source", "destination"]

    def clean(self) -> None:
        if self.source == self.destination:
            raise ValidationError("Source and destination can't be the same")

    def save(self, *args, **kwargs) -> "Route":
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.source.name} - {self.destination.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


def image_file_path(instance: Union["Train", "Crew"], filename: str) -> str:
    _, extension = os.path.splitext(filename)
    upload_to = "uploads/others/"
    name = "unknown"

    if isinstance(instance, Train):
        upload_to = "uploads/trains/"
        name = instance.name or "train"
    elif isinstance(instance, Crew):
        upload_to = "uploads/crew/"
        name = instance.full_name or "unknown"

    filename = f"{slugify(name)}-{uuid.uuid4()}{extension}"

    return os.path.join(upload_to, filename)


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )
    image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=image_file_path)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.full_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    crew = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def clean(self) -> None:
        if self.departure_time >= self.arrival_time:
            raise ValidationError(
                "Departure time cannot be later than or equal to arrival time"
            )

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.route.source.name} -> {self.route.destination.name} "
            f"Train: {self.train.name}"
        )


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["journey", "cargo", "seat"]

    @staticmethod
    def validate_ticket(
            cargo: int,
            seat: int,
            train: Train,
            error_to_raise: Type[ValidationError]
    ) -> None:
        if not (1 <= cargo <= train.cargo_num):
            raise error_to_raise(
                {
                    "cargo": f"Cargo number must be in available range: "
                             f"(1, {train.cargo_num})"
                }
            )
        if not (1 <= seat <= train.places_in_cargo):
            raise error_to_raise(
                {
                    "seat": f"Seat number must be in available range: "
                            f"(1, {train.places_in_cargo})"
                }
            )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(self, *args, **kwargs) -> "Ticket":
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Route: {str(self.journey.route)} "
            f"Cargo: {self.cargo}, Seat: {self.seat}"
        )
