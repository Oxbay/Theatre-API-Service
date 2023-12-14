import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, Performance, TheatreHall, Genre, Actor
from theatre.serializers import PlayDetailSerializer, PlayListSerializer

PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "Krist", "last_name": "Bloody"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(name="Blue", rows=20, seats_in_row=20)

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    """Return URL for recipe image upload"""
    return reverse("theatre:play-upload-image", args=[play_id])


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class PlayImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.performance = sample_performance(play=self.play)

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):
        """Test uploading an image to play"""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.play.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_play_list(self):
        url = PLAY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "genres": [1],
                    "actors": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Title")
        self.assertFalse(play.image)

    def test_image_url_is_shown_on_play_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.play.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_play_list(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PLAY_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_performance_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PERFORMANCE_URL)

        self.assertIn("play_image", res.data[0].keys())


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user1@user.com", password="user1pass"
        )

        self.client.force_authenticate(self.user)

    def test_list_of_plays(self):
        response = self.client.get(PLAY_URL)

        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_play_detail(self):
        temp_play = sample_play()
        url = detail_url(temp_play.id)
        response = self.client.get(url)
        serializer = PlayDetailSerializer(temp_play)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_of_plays_with_filtering_by_title(self):
        test_play1 = sample_play(title="PlayTitle")
        test_play2 = sample_play(title="Test")

        response = self.client.get(PLAY_URL, {"title": "te"})

        serializer1 = PlayListSerializer(test_play1)
        serializer2 = PlayListSerializer(test_play2)

        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer1.data, response.data)

    def test_list_of_plays_with_filtering_by_genre(self):
        temp_genre1 = sample_genre(name="Biba")
        temp_genre2 = sample_genre(name="Boba")
        temp_play1 = sample_play()
        temp_play2 = sample_play()
        temp_play1.genres.add(temp_genre1)
        temp_play2.genres.add(temp_genre2)

        res = self.client.get(PLAY_URL, {"genres": f"{temp_genre1.id}"})

        serializer1 = PlayListSerializer(temp_play1)
        serializer2 = PlayListSerializer(temp_play2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_list_of_plays_with_filtering_by_actor(self):
        temp_play1 = sample_play()
        temp_play2 = sample_play()
        temp_actor1 = sample_actor()
        temp_actor2 = sample_actor(first_name="Ruslan")
        temp_play1.actors.add(temp_actor1)
        temp_play2.actors.add(temp_actor2)

        response = self.client.get(PLAY_URL, {"actors": f"{temp_actor1.id}"})

        serializer1 = PlayListSerializer(temp_play1)
        serializer2 = PlayListSerializer(temp_play2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)
