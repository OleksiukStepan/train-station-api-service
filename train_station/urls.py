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

router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("trains", TrainViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("crews", CrewViewSet)
router.register("journeys", JourneyViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
