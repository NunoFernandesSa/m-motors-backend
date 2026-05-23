from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from folders.models import Folder
from folders.serializers import DocumentSerializer, FolderSerializer, FolderCreateSerializer
from folders.permissions import IsOwnerOrCommercial, CanValidateFolder
from rest_framework.parsers import MultiPartParser, FormParser
from .admin import Document


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


class FolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a folder.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrCommercial | CanValidateFolder]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()
    http_method_names = ['get', 'patch']


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
