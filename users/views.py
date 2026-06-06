from rest_framework import generics, status
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema_view, extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView


@extend_schema_view(
    create=extend_schema(
        summary="Inscription d'un nouvel utilisateur",
        description="Crée un compte utilisateur avec le rôle 'user' par défaut. Retourne les tokens JWT (access + refresh).",
        tags=["users"],
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="Utilisateur créé avec succès",
                response={
                    "type": "object",
                    "properties": {
                        "user": UserSerializer,
                        "message": {"type": "string"},
                        "refresh": {"type": "string"},
                        "access": {"type": "string"},
                    }
                }
            ),
            400: OpenApiResponse(description="Erreur de validation (ex: mots de passe non identiques, email déjà utilisé)"),
        },
        examples=[
            OpenApiExample(
                "Requête valide",
                value={
                    "username": "john_doe",
                    "email": "john@example.com",
                    "password": "Azerty123!",
                    "password2": "Azerty123!"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Réponse réussie",
                value={
                    "user": {"id": 1, "username": "john_doe", "email": "john@example.com"},
                    "message": "Utilisateur enregistré avec succès.",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                response_only=True,
            )
        ]
    )
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
    get=extend_schema(
        summary="Obtenir le profil",
        description="Retourne les informations de l'utilisateur authentifié.",
        tags=["users"],
        responses={200: UserSerializer, 401: OpenApiResponse(description="Non authentifié")}
    ),
    put=extend_schema(
        summary="Mettre à jour tout le profil",
        description="Remplace l'intégralité du profil de l'utilisateur connecté.",
        tags=["users"],
        request=UserSerializer,
        responses={200: UserSerializer, 400: OpenApiResponse(description="Erreur de validation")}
    ),
    patch=extend_schema(
        summary="Mise à jour partielle",
        description="Modifie uniquement les champs fournis dans la requête.",
        tags=["users"],
        request=UserSerializer,
        responses={200: UserSerializer, 400: OpenApiResponse(description="Erreur de validation")}
    )
)
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve the current authenticated user's details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer 

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            # Access token (5 minutes)
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,  # True on production (HTTPS)
                samesite='Lax',
                max_age=300,   # 5 minutes
                path='/',
            )
            # Refresh token (1 day)
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=False,  # True on production (HTTPS)
                samesite='Lax',
                max_age=86400,
                path='/',
            )
            # Remove the tokens from the JSON body for added security.
            response.data = {'message': 'Connexion réussie'}
        return response

@extend_schema_view(
    post=extend_schema(
        summary="Déconnexion",
        description="Supprime les cookies d'authentification pour déconnecter l'utilisateur.",
        tags=["users"],
        responses={200: OpenApiResponse(description="Déconnexion réussie")}
    )
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"message": "Déconnexion réussie"})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
