from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import Station, Route
from train_station.serializers import (
    RouteListSerializer,
    RouteDetailSerializer,
)

ROUTE_URL = reverse("station:route-list")


def sample_station(name: str) -> Station:
    return Station.objects.create(name=name)

def sample_route(**params) -> Route:
    defaults = {
        "source": sample_station("Lviv"),
        "destination": sample_station("Kyiv"),
        "distance": 540,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)

def detail_url(route_id: int) -> str:
    return reverse("station:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_route_list(self) -> None:
        sample_route()
        sample_route(
            source=sample_station("Kharkiv"),
            destination=sample_station("Odessa")
        )

        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all().order_by("-id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_route_detail(self) -> None:
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)
        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_create_route_forbidden(self) -> None:
        payload = {
            "source": sample_station("Lviv").id,
            "destination": sample_station("Kyiv").id,
            "distance": 540,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_routes_by_source_and_destination(self) -> None:
        route1 = sample_route(
            source=sample_station("Lviv"),
            destination=sample_station("Kyiv")
        )
        route2 = sample_route(
            source=sample_station("Kharkiv"),
            destination=sample_station("Odessa")
        )

        res = self.client.get(
            ROUTE_URL, {"source": "Lviv", "destination": "Kyiv"}
        )
        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_order_routes_by_distance(self) -> None:
        route1 = sample_route(
            source=sample_station("Lviv"),
            destination=sample_station("Kyiv"),
            distance=540
        )
        route2 = sample_route(
            source=sample_station("Kharkiv"),
            destination=sample_station("Odessa"),
            distance=730
        )

        res = self.client.get(ROUTE_URL, {"ordering": "distance"})
        routes = Route.objects.all().order_by("distance")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AdminRouteTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin_test@test.com", password="test_admin", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self) -> None:
        source = sample_station("Lviv")
        destination = sample_station("Kyiv")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 540,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Route.objects.filter(
                source=source, destination=destination, distance=540
            ).exists()
        )

    def test_delete_route(self) -> None:
        route = sample_route()
        url = detail_url(route.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Route.objects.filter(id=route.id).exists())

    def test_update_route(self) -> None:
        route = sample_route()
        url = detail_url(route.id)
        payload = {
            "source": route.source.id,
            "destination": route.destination.id,
            "distance": 600,
        }
        res = self.client.put(url, payload, format="json")
        route.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(route.distance, 600)

    def test_partial_update_route(self) -> None:
        route = sample_route()
        url = detail_url(route.id)
        payload = {"distance": 580}
        res = self.client.patch(url, payload, format="json", partial=True)
        route.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(route.distance, 580)
