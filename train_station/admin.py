from django.contrib import admin

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


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    list_filter = ("source", "destination")
    search_fields = ("source__name", "destination__name")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)
    list_filter = ("created_at",)


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("name", "train_type", "cargo_num", "places_in_cargo")
    search_fields = ("name", "train_type__name")
    list_filter = ("train_type",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("first_name", "last_name")


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ("route", "train", "departure_time", "arrival_time")
    list_filter = ("route", "train", "departure_time")
    search_fields = ("route__source__name", "route__destination__name", "train__name")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("journey", "cargo", "seat", "order")
    list_filter = ("journey", "cargo", "seat")
    search_fields = (
        "order__user__username",
        "journey__route__source__name",
        "journey__route__destination__name",
    )
