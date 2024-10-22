from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import TrainType
from train_station.serializers import TrainTypeSerializer

TRAIN_TYPE_URL = reverse("station:traintype-list")


def sample_train_type(**params) -> TrainType:
    defaults = {"name": "Test Train Type"}
    defaults.update(params)
    return TrainType.objects.create(**defaults)

def detail_url(train_type_id: int) -> str:
    return reverse("station:traintype-detail", args=[train_type_id])


class UnauthenticatedTrainTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_train_type_list(self) -> None:
        sample_train_type()
        sample_train_type(name="Another Train Type")

        res = self.client.get(TRAIN_TYPE_URL)
        train_types = TrainType.objects.all().order_by("-id")
        serializer = TrainTypeSerializer(train_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_train_type_detail(self) -> None:
        train_type = sample_train_type()

        url = detail_url(train_type.id)
        res = self.client.get(url)
        serializer = TrainTypeSerializer(train_type)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_train_type_list_ordering(self) -> None:
        sample_train_type(name="A Train Type")
        sample_train_type(name="B Train Type",)

        res = self.client.get(TRAIN_TYPE_URL, {"ordering": "name"})
        stations = TrainType.objects.all().order_by("name")
        serializer = TrainTypeSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_user_create_train_type_forbidden(self) -> None:
        payload = {"name": "New Train Type"}
        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@admin.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train_type(self) -> None:
        payload = {"name": "New Train Type"}
        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TrainType.objects.filter(name="New Train Type").exists()
        )

    def test_delete_train_type(self) -> None:
        train_type = sample_train_type()
        url = detail_url(train_type.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TrainType.objects.filter(id=train_type.id).exists())

    def test_update_train_type(self) -> None:
        train_type = sample_train_type()
        url = detail_url(train_type.id)
        payload = {"name": "Updated Train Type"}
        res = self.client.put(url, payload, format="json")
        train_type.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(train_type.name, "Updated Train Type")

    def test_partial_update_train_type(self) -> None:
        train_type = sample_train_type()
        url = detail_url(train_type.id)
        payload = {"name": "Partially Updated"}
        res = self.client.patch(url, payload, format="json")
        train_type.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(train_type.name, "Partially Updated")
