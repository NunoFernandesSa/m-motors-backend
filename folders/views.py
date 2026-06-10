from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from folders.models import Folder, Document
from folders.serializers import DocumentSerializer, FolderSerializer, FolderCreateSerializer
from folders.permissions import IsOwnerOrCommercial, CanValidateFolder
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample


@extend_schema_view(
    get=extend_schema(
        summary="Liste des dossiers",
        description="Retourne les dossiers selon le rôle : pour un client → ses propres dossiers ; pour un commercial/admin → tous les dossiers.",
        tags=["folders"],
        responses={200: FolderSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Soumettre un dossier",
        description="Crée un nouveau dossier d'achat/location pour un véhicule. Statut initial 'pending'. Les documents seront ajoutés ultérieurement via l'endpoint dédié.",
        tags=["folders"],
        request=FolderCreateSerializer,
        responses={
            201: FolderSerializer,
            400: OpenApiResponse(description="Erreur de validation (véhicule indisponible, etc.)"),
            401: OpenApiResponse(description="Non authentifié"),
        },
        examples=[
            OpenApiExample(
                "Requête valide",
                value={"vehicle": 1},
                request_only=True,
            ),
            OpenApiExample(
                "Réponse réussie",
                value={
                    "id": 1,
                    "status": "pending",
                    "vehicle": 1,
                    "user": 2,
                    "created_at": "2025-05-23T10:00:00Z",
                    "comment": "",
                    "document_files": [],
                },
                response_only=True,
            )
        ]
    )
)
class FolderListCreateView(generics.ListCreateAPIView):
    """
    API view to list all folders of the authenticated user and to create a new folder.
    """

    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the folders of the authenticated user or all folders if the user is a commercial or admin.
        """

        user = self.request.user
        if user.groups.filter(name__in=['commercial', 'admin']).exists():
            return Folder.objects.all()
        
        return Folder.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request method.
        """

        if self.request.method == 'POST':
            return FolderCreateSerializer
        
        return FolderSerializer

    def perform_create(self, serializer):
        """
        Set the user of the folder to the authenticated user when creating a new folder.
        """

        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Détail d'un dossier",
        description="Retourne les informations complètes d'un dossier, incluant les documents associés.",
        tags=["folders"],
        responses={200: FolderSerializer, 403: OpenApiResponse(description="Accès interdit")},
    ),
    patch=extend_schema(
        summary="Mettre à jour un dossier (partiel)",
        description="Permet de modifier le commentaire ou d'autres champs (sauf statut). Pour valider un dossier, utilisez l'endpoint dédié `/validate/`.",
        tags=["folders"],
        request=FolderSerializer,
        responses={200: FolderSerializer},
    ),
)
class FolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a folder.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrCommercial]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()
    http_method_names = ['get', 'patch', 'delete']


@extend_schema_view(
    patch=extend_schema(
        summary="Valider ou refuser un dossier",
        description="Change le statut d'un dossier ('approved' ou 'rejected'). Un commentaire peut être ajouté. Réservé aux utilisateurs ayant la permission `can_validate_folder` (commerciaux/admin).",
        tags=["folders"],
        request={
            "application/json": {
                "status": "approved",
                "comment": "Dossier complet, accepté."
            }
        },
        responses={200: FolderSerializer, 400: OpenApiResponse(description="Statut invalide"), 403: OpenApiResponse(description="Permission non accordée")},
        examples=[
            OpenApiExample(
                "Validation acceptée",
                value={"status": "approved", "comment": "Dossier conforme"},
                request_only=True,
            ),
            OpenApiExample(
                "Refus avec motif",
                value={"status": "rejected", "comment": "Documents manquants"},
                request_only=True,
            )
        ]
    )
)
class FolderValidateView(generics.UpdateAPIView):
    """
    API view to validate a folder by changing its status to 'approved' or 'rejected' and optionally adding a comment.
    """

    permission_classes = [IsAuthenticated, CanValidateFolder]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        """
        Validate a folder by changing its status to 'approved' or 'rejected' and optionally adding a comment.
        """

        folder = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')

        if new_status not in ['approved', 'rejected']:
            return Response({'error': "Le status doit être 'approved' ou 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        
        folder.status = new_status

        if comment:
            folder.validation_comment = comment

        folder.save()

        serializer = self.get_serializer(folder)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Uploader un document",
        description="Ajoute un fichier (PDF, PNG, JPG, JPEG) à un dossier existant. L'utilisateur doit être propriétaire du dossier ou commercial/admin.",
        tags=["folders"],
        parameters=[
            OpenApiParameter(name="folder_pk", type=int, location=OpenApiParameter.PATH, description="ID du dossier"),
        ],
        responses={201: DocumentSerializer, 400: OpenApiResponse(description="Type de fichier non autorisé"), 403: OpenApiResponse(description="Accès interdit")},
        examples=[
            OpenApiExample(
                "Requête d'upload",
                value={"file": "(fichier binaire)"},
                request_only=True,
            )
        ]
    )
)
class DocumentUploadView(generics.CreateAPIView):
    """
    API view to upload a document to a folder.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrCommercial]
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """
        Set the folder of the document based on the URL parameter and check permissions.
        """

        folder_id = self.kwargs.get('folder_pk')
        folder = Folder.objects.get(pk=folder_id)

        if self.request.user != folder.user and not self.request.user.groups.filter(name__in=['commercial', 'admin']).exists():
            raise self.permission_denied("Vous n'avez pas accès à ce dossier.")
        
        serializer.save(folder=folder)
