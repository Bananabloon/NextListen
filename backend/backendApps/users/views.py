from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Genre, PreferenceVector
from .serializers import RegisterSerializer, UserSerializer, PreferenceVectorSerializer

User = get_user_model()



class PreferenceVectorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vectors = PreferenceVector.objects.filter(user=request.user)
        serializer = PreferenceVectorSerializer(vectors, many=True)
        return Response(serializer.data)

    def post(self, request):
        genre_name = request.data.get("genre")
        preferences = request.data.get("preferences")

        if not genre_name or preferences is None:
            return Response({"error": "Genre and preferences are required."}, status=400)

        genre = Genre.objects.filter(name=genre_name).first()
        if not genre:
            return Response({"error": "Genre not found."}, status=400)

        vector, _ = PreferenceVector.objects.update_or_create(
            user=request.user,
            genre=genre,
            defaults={"preferences": preferences}
        )

        serializer = PreferenceVectorSerializer(vector)
        return Response({
            "message": "Preferences updated",
            "data": serializer.data
        })
