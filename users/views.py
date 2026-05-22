from rest_framework import generics, status
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    post=extend_schema(description="Enregistrer un nouvel utilisateur")
)
class RegisterView(generics.CreateAPIView):
    """
    Endpoint for new user registration.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        default_group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(default_group)
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Utilisateur enregistré avec succès.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(description="Récupérer le profil de l'utilisateur connecté"),
    put=extend_schema(description="Mettre à jour le profil complet"),
    patch=extend_schema(description="Mise à jour partielle du profil"),
)
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve the current authenticated user's details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer 

    def get_object(self):
        return self.request.user
