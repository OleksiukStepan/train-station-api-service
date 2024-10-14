from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import (
    Ticket,
    Journey,
    Train,
    TrainType,
    Route,
    Order,
    Station
)
from train_station.serializers import (
    TicketListSerializer,
    TicketDetailSerializer
)
from django.utils.timezone import make_aware
import datetime

TICKETS_URL = reverse("station:ticket-list")


def sample_station(name: str) -> Station:
    return Station.objects.create(name=name)

def sample_route(source: str = "Lviv", destination: str = "Kyiv") -> Route:
    return Route.objects.get_or_create(
        source=sample_station(source),
        destination=sample_station(destination),
        distance=540
    )[0]

def sample_train_type(name: str = "Test Type") -> TrainType:
    return TrainType.objects.get_or_create(name=name)[0]

def sample_train(name: str = "Test Train") -> Train:
    return Train.objects.get_or_create(
        name=name,
        cargo_num=10,
        places_in_cargo=20,
        train_type=sample_train_type()
    )[0]

def sample_journey(**params) -> Journey:
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": make_aware(
            datetime.datetime(2024, 10, 10, 10, 0)
        ),
        "arrival_time": make_aware(
            datetime.datetime(2024, 10, 10, 16, 0)
        ),
    }
    defaults.update(params)
    return Journey.objects.get_or_create(**defaults)[0]

def sample_order(user) -> Order:
    return Order.objects.create(user=user)

def sample_ticket(order: Order, **params) -> Ticket:
    defaults = {
        "cargo": 1,
        "seat": 1,
        "journey": sample_journey(),
    }
    defaults.update(params)
    return Ticket.objects.create(order=order, **defaults)

def detail_url(ticket_id: int) -> str:
    return reverse("station:ticket-detail", args=[ticket_id])


class UnauthenticatedTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(TICKETS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="password"
        )
        self.client.force_authenticate(self.user)
        self.order = sample_order(user=self.user)
        self.journey = sample_journey()

    def test_ticket_list(self) -> None:
        sample_ticket(order=self.order)
        sample_ticket(order=self.order, cargo=2, seat=2)

        res = self.client.get(TICKETS_URL)
        tickets = Ticket.objects.all().order_by("-id")
        serializer = TicketListSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_ticket_detail(self) -> None:
        ticket = sample_ticket(order=self.order)

        url = detail_url(ticket.id)
        res = self.client.get(url)
        serializer = TicketDetailSerializer(ticket)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_order_tickets_by_cargo_and_seat(self) -> None:
        sample_ticket(order=self.order, cargo=1, seat=1)
        sample_ticket(order=self.order, cargo=1, seat=2)
        sample_ticket(order=self.order, cargo=2, seat=1)

        res = self.client.get(TICKETS_URL, {"ordering": "cargo,seat"})
        tickets = Ticket.objects.all().order_by("cargo", "seat")
        serializer = TicketListSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AdminTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.order = sample_order(user=self.user)
        self.journey = sample_journey()

    def test_create_ticket(self) -> None:
        order_url = reverse("station:order-list")
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,
                }
            ]
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(order_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        new_order = Order.objects.latest("id")
        self.assertEqual(new_order.user, self.user)
        self.assertEqual(new_order.tickets.count(), 1)
        ticket = new_order.tickets.first()
        self.assertEqual(ticket.cargo, 1)
        self.assertEqual(ticket.seat, 1)
        self.assertEqual(ticket.journey, self.journey)

    def test_update_ticket(self) -> None:
        ticket = sample_ticket(order=self.order)
        payload = {
            "cargo": 2,
            "seat": 3,
            "journey": self.journey.id
        }

        url = detail_url(ticket.id)
        res = self.client.put(url, payload, format="json")
        ticket.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ticket.cargo, 2)
        self.assertEqual(ticket.seat, 3)

    def test_partial_update_ticket(self) -> None:
        ticket = sample_ticket(order=self.order)
        payload = {
            "seat": 4,
            "cargo": ticket.cargo,
            "journey": ticket.journey.id
        }

        url = detail_url(ticket.id)
        res = self.client.patch(url, payload, format="json")
        ticket.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ticket.seat, 4)

    def test_delete_ticket(self) -> None:
        ticket = sample_ticket(order=self.order)

        url = detail_url(ticket.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())
