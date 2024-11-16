from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import Order
from train_station.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
)

ORDER_URL = reverse("station:order-list")

def sample_order(user) -> Order:
    return Order.objects.create(user=user)

def detail_url(order_id: int) -> str:
    return reverse("station:order-detail", args=[order_id])


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_order_list(self) -> None:
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)
        orders = Order.objects.filter(user=self.user).order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_order_detail(self) -> None:
        order = sample_order(user=self.user)

        url = detail_url(order.id)
        res = self.client.get(url)
        serializer = OrderDetailSerializer(order)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_filter_orders_by_created_at(self) -> None:
        order1 = sample_order(user=self.user)
        order2 = sample_order(user=self.user)
        order2.created_at = '10-10-14 17:38:47'

        res = self.client.get(
            ORDER_URL,
            {"created_at": order1.created_at.strftime("%Y-%m-%d")}
        )
        serializer1 = OrderListSerializer(order1)
        serializer2 = OrderListSerializer(order2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_order_orders_by_created_at(self) -> None:
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL, {"ordering": "created_at"})
        orders = Order.objects.filter(user=self.user).order_by("created_at")
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AdminOrderTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin_test@test.com", password="test_admin", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_delete_order(self) -> None:
        order = sample_order(user=self.user)
        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())
