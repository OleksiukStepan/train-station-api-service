from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from train_station.models import Crew
from train_station.serializers import CrewSerializer

CREW_URL = reverse("station:crew-list")


def sample_crew(**params) -> Crew:
    defaults = {"first_name": "Test", "last_name": "Crew"}
    defaults.update(params)
    return Crew.objects.create(**defaults)

def detail_url(crew_id: int) -> str:
    return reverse("station:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_crew_list(self) -> None:
        sample_crew()
        sample_crew(first_name="Another", last_name="Crew")

        res = self.client.get(CREW_URL)
        crew_members = Crew.objects.all().order_by("-id")
        serializer = CrewSerializer(crew_members, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_crew_detail(self) -> None:
        crew = sample_crew()

        url = detail_url(crew.id)
        res = self.client.get(url)
        serializer = CrewSerializer(crew)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_create_crew_forbidden(self) -> None:
        payload = {"first_name": "New", "last_name": "Crew"}
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@admin.com", password="password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self) -> None:
        payload = {"first_name": "New", "last_name": "Crew"}
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Crew.objects.filter(first_name="New", last_name="Crew").exists()
        )

    def test_delete_crew(self) -> None:
        crew = sample_crew()
        url = detail_url(crew.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Crew.objects.filter(id=crew.id).exists())

    def test_update_crew(self) -> None:
        crew = sample_crew()
        url = detail_url(crew.id)
        payload = {"first_name": "Updated", "last_name": "Crew"}
        res = self.client.put(url, payload, format="json")
        crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(crew.first_name, "Updated")
        self.assertEqual(crew.last_name, "Crew")

    def test_partial_update_crew(self) -> None:
        crew = sample_crew()
        url = detail_url(crew.id)
        payload = {"first_name": "Partially Updated"}
        res = self.client.patch(url, payload, format="json")
        crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(crew.first_name, "Partially Updated")
