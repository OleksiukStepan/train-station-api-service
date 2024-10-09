from django.db import models
from django.core.exceptions import ValidationError

from train_station_core import settings


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ["latitude", "longitude"]
        ordering = ["name"]

    def __str__(self):
        return (
            f"{self.name} "
            f"(lat: {self.latitude:.2f}, long: {self.longitude:.2f})"
        )


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        related_name="routes_from",
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station,
        related_name="routes_to",
        on_delete=models.CASCADE
    )
    distance = models.IntegerField()

    class Meta:
        unique_together = ["source", "destination"]

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination can't be the same")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.source.name} - {self.destination.name} "
                f"({self.distance} km)")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    def __str__(self):
        return (
            f"Train: {self.name} ({self.train_type.name}) - "
            f"Cargos: {self.cargo_num}, "
            f"Places per Cargo: {self.places_in_cargo}"
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
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

    def clean(self):
        if self.departure_time >= self.arrival_time:
            raise ValidationError(
                "Departure time cannot be later than or equal to arrival time"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{str(self.route)}\n"
            f"{str(self.train)}\n"
            f"Departure: {self.departure_time} - "
            f"Arrival: {self.arrival_time}"
        )


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["journey", "cargo", "seat"]

    def __str__(self):
        return (
            f"Route: {str({self.journey.route})} "
            f"Cargo: {self.cargo}, Seat: {self.seat} \n"
            f"Departure: {self.journey.departure_time} - "
            f"Arrival: {self.journey.arrival_time}"
            f"Order time: {self.order}"
        )