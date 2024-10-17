import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import (
    Journey,
    Route,
    TrainType,
    Train,
    Crew,
    Station
)
from train_station.serializers import (
    JourneyListSerializer,
    JourneyDetailSerializer
)

JOURNEY_URL = reverse("station:journey-list")


def sample_route(source: str = "Lviv", destination: str = "Kyiv") -> Route:
    return Route.objects.create(
        source=Station.objects.create(name=source),
        destination=Station.objects.create(name=destination),
        distance=540
    )


def sample_train_type(name: str = "Test Type") -> TrainType:
    return TrainType.objects.get_or_create(name=name)[0]


def sample_train(name: str = "Test Train") -> Train:
    return Train.objects.get_or_create(
        name=name,
        cargo_num=10,
        places_in_cargo=20,
        train_type=sample_train_type()
    )[0]


def sample_crew(first_name: str = "Test", last_name: str = "Crew") -> Crew:
    return Crew.objects.create(first_name=first_name, last_name=last_name)


def sample_journey(**params) -> Journey:
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": make_aware(
            datetime.datetime(
                2024, 10, 10, 10, 0
            )
        ),
        "arrival_time": make_aware(
            datetime.datetime(
                2024, 10, 10, 16, 0
            )
        ),
    }
    defaults.update(params)
    journey = Journey.objects.create(**defaults)
    journey.tickets_available = (
            journey.train.cargo_num * journey.train.places_in_cargo
            - journey.tickets.count()
    )
    return journey


def detail_url(journey_id: int) -> str:
    return reverse("station:journey-detail", args=[journey_id])


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_journey_list(self) -> None:
        sample_journey()
        sample_journey(
            route=sample_route(source="Kharkiv", destination="Odessa"),
            train=sample_train(name="Test Train 2")
        )

        res = self.client.get(JOURNEY_URL)
        journeys = Journey.objects.annotate(
            tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count("tickets")
            )
        ).order_by("-id")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_journey_detail(self) -> None:
        journey = sample_journey()

        url = detail_url(journey.id)
        res = self.client.get(url)
        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_journeys_by_departure_and_arrival_time(self) -> None:
        journey1 = sample_journey(
            departure_time="2024-10-10 08:00:00",
            arrival_time="2024-10-10 14:00:00"
        )
        journey2 = sample_journey(
            departure_time="2024-10-11 09:00:00",
            arrival_time="2024-10-11 15:00:00"
        )

        res = self.client.get(
            JOURNEY_URL, {"departure_time": "2024-10-10"}
        )
        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_order_journeys_by_departure_time(self) -> None:
        sample_journey(
            departure_time=make_aware(
                datetime.datetime(
                    2024, 10, 10, 8, 0
                )
            )
        )
        sample_journey(
            departure_time=make_aware(
                datetime.datetime(
                    2024, 10, 10, 9, 0
                )
            )
        )

        res = self.client.get(JOURNEY_URL, {"ordering": "departure_time"})
        journeys = Journey.objects.annotate(
            tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count("tickets")
            )
        ).order_by("departure_time")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AdminJourneyApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_journey(self) -> None:
        route = sample_route()
        train = sample_train()
        crew = sample_crew()
        payload = {
            "route": route.id,
            "train": train.id,
            "crew": crew.id,
            "departure_time": "2024-10-11 08:00:00",
            "arrival_time": "2024-10-11 12:00:00",
        }

        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Journey.objects.filter(
                route=route, train=train, departure_time="2024-10-11 08:00:00"
            ).exists()
        )

    def test_update_journey(self) -> None:
        journey = sample_journey()
        route = sample_route(source="Kharkiv", destination="Odessa")
        crew = sample_crew()
        payload = {
            "train": journey.train.id,
            "crew": [crew.id],
            "route": route.id,
            "departure_time": journey.departure_time,
            "arrival_time": journey.arrival_time,
        }

        url = detail_url(journey.id)
        res = self.client.put(url, payload, format="json")
        journey.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(journey.crew.filter(id=crew.id).exists())
        self.assertEqual(journey.route, route)


    def test_partial_update_journey(self) -> None:
        journey = sample_journey()
        payload = {
            "departure_time": "2024-10-09T10:00:00Z",
            "arrival_time": "2024-11-09T11:00:00Z"
        }

        url = detail_url(journey.id)
        res = self.client.patch(url, payload, format="json", partial=True)
        journey.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            journey.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
            "2024-10-09 10:00:00"
        )
        self.assertEqual(
            journey.arrival_time.strftime("%Y-%m-%d %H:%M:%S"),
            "2024-11-09 11:00:00"
        )


    def test_delete_journey(self) -> None:
        journey = sample_journey()

        url = detail_url(journey.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Journey.objects.filter(id=journey.id).exists())
