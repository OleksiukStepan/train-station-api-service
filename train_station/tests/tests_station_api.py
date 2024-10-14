from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Station
from train_station.serializers import StationSerializer

STATION_URL = reverse("station:station-list")


def sample_station(**params) -> Station:
    default = {
        "name": "Test Station",
        "latitude": 11.1111,
        "longitude": 22.2222,
    }
    default.update(params)
    return Station.objects.create(**default)


def detail_url(station_id: int) -> str:
    return reverse("station:station-detail", args=[station_id])


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_station_list(self) -> None:
        sample_station()
        sample_station(
            name="Test Station 2",
            latitude=22.2222,
            longitude=33.3333,
        )


        res = self.client.get(STATION_URL)
        stations = Station.objects.all().order_by("-id")
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_station_detail(self) -> None:
        station = sample_station()

        url = detail_url(station.id)
        res = self.client.get(url)
        serializer = StationSerializer(station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_station_list_ordering(self) -> None:
        station1 = sample_station(
            name="A Station",
            latitude=22.2222,
            longitude=33.3333,
        )
        station2 = sample_station(
            name="B Station",
            latitude=23.2222,
            longitude=34.3333,
        )

        res = self.client.get(STATION_URL, {"ordering": "name"})
        stations = Station.objects.all().order_by("name")
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_user_create_station_forbidden(self) -> None:
        payload = {"name": "New Station"}
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@admin.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self) -> None:
        payload = {
            "name": "New Station",
            "latitude": 33.3333,
            "longitude": 44.4444,
        }
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Station.objects.filter(name="New Station").exists())

    def test_delete_station(self) -> None:
        station = sample_station()
        url = detail_url(station.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Station.objects.filter(id=station.id).exists())

    def test_update_station(self) -> None:
        station = sample_station()
        url = detail_url(station.id)
        payload = {
            "name": "Updated Station",
            "latitude": 22.2222,
            "longitude": 33.3333,
        }
        res = self.client.put(url, payload, format="json")
        station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(station.name, "Updated Station")

    def test_partial_update_station(self) -> None:
        station = sample_station()
        url = detail_url(station.id)
        payload = {
            "name": "Partially Updated Station",
            "latitude": 22.2222,
            "longitude": 33.3333,
        }
        res = self.client.patch(url, payload, format="json")
        station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(station.name, "Partially Updated Station")
