import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import TrainType, Train, Crew

TRAIN_URL = reverse("station:train-list")
CREW_URL = reverse("station:crew-list")


def sample_train(**params) -> Train:
    default = {
        "name": "Test Train",
        "cargo_num": 10,
        "places_in_cargo": 10,
        "train_type": TrainType.objects.create(name="Test Type"),
    }
    default.update(params)
    return Train.objects.create(**default)


def sample_crew(**params) -> Crew:
    default = {"first_name": "Test", "last_name": "Crew"}
    default.update(params)
    return Crew.objects.create(**default)


def image_upload_url(instance_id: int, model_name: str) -> str:
    return reverse(
        f"station:{model_name}-upload-image", args=[instance_id]
    )


def detail_url(instance_id: int, model_name: str) -> str:
    return reverse(f"station:{model_name}-detail", args=[instance_id])


class TestUploadImageMixin(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "test@admin.com", "password",
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()
        self.crew = sample_crew()

    def tearDown(self) -> None:
        self.train.image.delete()
        self.crew.image.delete()

    def test_upload_image_to_train(self) -> None:
        url = image_upload_url(self.train.id, "train")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url, {"image": ntf}, format="multipart"
            )
        self.train.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_upload_image_to_crew(self) -> None:
        url = image_upload_url(self.crew.id, "crew")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url, {"image": ntf}, format="multipart"
            )
        self.crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.crew.image.path))

    def test_upload_image_bad_request(self) -> None:
        url = image_upload_url(self.train.id, "train")
        res = self.client.post(
            url, {"image": "not image"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_unauthorized(self) -> None:
        self.client.logout()
        url = image_upload_url(self.train.id, "train")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url, {"image": ntf}, format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_image_forbidden(self) -> None:
        user = get_user_model().objects.create_user(
            "test@user.com", "password"
        )
        self.client.force_authenticate(user)
        url = image_upload_url(self.train.id, "train")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url, {"image": ntf}, format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_image_to_train_list(self) -> None:
        url = TRAIN_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Test Train 2",
                    "cargo_num": 10,
                    "places_in_cargo": 10,
                    "train_type": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(name="Test Train 2")
        self.assertFalse(train.image)

    def test_image_url_is_shown_on_train_detail(self) -> None:
        url = image_upload_url(self.train.id, "train")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.train.id, "train"))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_train_list(self) -> None:
        url = image_upload_url(self.train.id, "train")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(TRAIN_URL)

        self.assertIn("image", res.data["results"][0].keys())

    def test_image_url_is_shown_on_crew_detail(self) -> None:
        url = image_upload_url(self.crew.id, "crew")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.crew.id, "crew"))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_crew_list(self) -> None:
        url = image_upload_url(self.crew.id, "crew")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(CREW_URL)

        self.assertIn("image", res.data["results"][0].keys())
