from rest_framework.test import APITestCase
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            spotify_user_id="test_user_id", display_name="Test User"
        )

    def test_register_user(self):
        data = {"spotify_user_id": "new_user", "display_name": "New User"}
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["spotify_user_id"], "new_user")

    def test_me_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        response = self.client.get("/users/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["spotify_user_id"], "test_user_id")

    def test_me_unauthenticated(self):
        response = self.client.get("/users/me/")
        self.assertEqual(response.status_code, 401)
