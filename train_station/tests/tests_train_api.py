from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import Train, TrainType
from train_station.serializers import TrainListSerializer, TrainDetailSerializer

TRAIN_URL = reverse("station:train-list")


def sample_train_type(name: str = "Test Type") -> TrainType:
    train_type, _ = TrainType.objects.get_or_create(name=name)
    return train_type

def sample_train(**params) -> Train:
    defaults = {
        "name": "Test Train",
        "cargo_num": 10,
        "places_in_cargo": 20,
        "train_type": sample_train_type(),
    }
    defaults.update(params)
    return Train.objects.create(**defaults)

def detail_url(train_id: int) -> str:
    return reverse("station:train-detail", args=[train_id])


class UnauthenticatedTrainApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="password"
        )
        self.client.force_authenticate(self.user)

    def test_train_list(self) -> None:
        print([type for type in TrainType.objects.all()])
        a = sample_train()
        b = sample_train(name="Test Train 2")

        res = self.client.get(TRAIN_URL)
        trains = Train.objects.all().order_by("-id")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_train_detail(self) -> None:
        train = sample_train()

        url = detail_url(train.id)
        res = self.client.get(url)
        serializer = TrainDetailSerializer(train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_trains_by_train_type(self) -> None:
        train_type1 = sample_train_type(name="Type A")
        train_type2 = sample_train_type(name="Type B")

        train1 = sample_train(name="Train 1", train_type=train_type1)
        train2 = sample_train(name="Train 2", train_type=train_type2)

        res = self.client.get(TRAIN_URL, {"train_type": train_type1.id})
        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_order_trains_by_name(self) -> None:
        sample_train(name="A Train")
        sample_train(name="B Train")

        res = self.client.get(TRAIN_URL, {"ordering": "name"})
        trains = Train.objects.all().order_by("name")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AdminTrainApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@admin.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train(self) -> None:
        train_type = sample_train_type()
        payload = {
            "name": "New Train",
            "cargo_num": 15,
            "places_in_cargo": 30,
            "train_type": train_type.id,
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Train.objects.filter(name="New Train").exists())

    def test_update_train(self) -> None:
        train = sample_train()
        train_type = sample_train_type(name="Updated Type")
        payload = {
            "name": "Updated Train",
            "cargo_num": 20,
            "places_in_cargo": 40,
            "train_type": train_type.id,
        }

        url = detail_url(train.id)
        res = self.client.put(url, payload, format="json")
        train.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(train.name, "Updated Train")
        self.assertEqual(train.cargo_num, 20)
        self.assertEqual(train.places_in_cargo, 40)
        self.assertEqual(train.train_type, train_type)

    def test_partial_update_train(self) -> None:
        train = sample_train()
        payload = {"name": "Partially Updated Train"}

        url = detail_url(train.id)
        res = self.client.patch(url, payload, format="json")
        train.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(train.name, "Partially Updated Train")

    def test_delete_train(self) -> None:
        train = sample_train()

        url = detail_url(train.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Train.objects.filter(id=train.id).exists())
