from django.urls import path, include
from rest_framework import routers

from train_station.views import (
    StationViewSet,
    RouteViewSet,
    OrderViewSet,
    TrainViewSet,
    TrainTypeViewSet,
    CrewViewSet,
    JourneyViewSet,
    TicketViewSet,
)


router = routers.DefaultRouter()

router.register("station", StationViewSet)
router.register("route", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("train", TrainViewSet)
router.register("train-type", TrainTypeViewSet)
router.register("crew", CrewViewSet)
router.register("journey", JourneyViewSet)
router.register("ticket", TicketViewSet)



urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
