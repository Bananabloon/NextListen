# import pytest
# from django.contrib.auth import get_user_model
# from authentication.services.spotify_service import SpotifyService
# from unittest.mock import patch

# User = get_user_model()

# @pytest.mark.django_db
# def test_get_profile_success():
#     user = User.objects.create(
#         spotify_user_id="abc123",
#         display_name="Test User",
#         spotify_access_token="valid_token"
#     )

#     mock_response = {
#         "id": "abc123",
#         "display_name": "Test User",
#         "country": "PL"
#     }

#     with patch("authentication.services.spotify_service.requests.get") as mock_get:
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = mock_response

#         spotify = SpotifyService()
#         profile = spotify.get_user_profile()

#         assert profile["id"] == "abc123"
#         assert profile["display_name"] == "Test User"
#         assert profile["country"] == "PL"
