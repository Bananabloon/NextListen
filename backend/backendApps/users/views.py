from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, PreferenceVector
from .serializers import RegisterSerializer, UserSerializer, PreferenceVectorSerializer


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
