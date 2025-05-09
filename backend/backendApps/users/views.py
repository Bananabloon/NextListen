from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .models import User, PreferenceVector
from .serializers import RegisterSerializer, UserSerializer, PreferenceVectorSerializer

User = get_user_model()

class SpotifyLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "No access token"}, status=400)

        # Znajdź użytkownika po tokenie (lepiej byłoby po ID)
        try:
            user = User.objects.get(spotifyAccessToken=access_token)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # default PreferenceVector:
        # PreferenceVector.objects.create(user=user, genreName=some_genre, preferences={})
        return user


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PreferenceVectorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vectors = PreferenceVector.objects.filter(user=request.user)
        serializer = PreferenceVectorSerializer(vectors, many=True)
        return Response(serializer.data)

    def post(self, request):
        genre_name = request.data.get("genreName")
        preferences = request.data.get("preferences")

        try:
            genre = Genre.objects.get(genreName=genre_name)
        except Genre.DoesNotExist:
            return Response({"error": "Genre not found"}, status=400)

        vector, created = PreferenceVector.objects.update_or_create(
            user=request.user,
            genreName=genre,
            defaults={"preferences": preferences}
        )
        return Response({"message": "Updated", "data": PreferenceVectorSerializer(vector).data})
