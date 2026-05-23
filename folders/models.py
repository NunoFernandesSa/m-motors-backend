from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle
import os
from django.db import models
from django.core.validators import FileExtensionValidator

def document_upload_path(instance, filename):
    """
    Generates a dynamic file path for uploaded documents based on the user and folder IDs.
    The path format is: 'documents/user_{user_id}/folder_{folder_id}/{filename}'.
    """
    return f'documents/user_{instance.folder.user.id}/folder_{instance.folder.id}/{filename}'


class Folder(models.Model):
    """
    Template representing a validation file for a vehicle rental request.
    """
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Validé'),
        ('rejected', 'Refusé'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # TODO: upload documents to S3 and store the URLs in the database
    documents = models.JSONField(default=list, help_text="Liste d'URLs des documents téléchargés")
    comment = models.TextField(blank=True, help_text="Motif de refus ou commentaire commercial")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----- Relations -----
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='folders')

    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['-created_at']
        permissions = [
            ("can_validate_folder", "Peut valider ou refuser un dossier"),
            ("can_view_all_folders", "Peut voir tous les dossiers clients"),
        ]

    def __str__(self):
        """
        Displays a readable representation of the folder, including the ID, user name, and associated vehicle.
        """
        
        return f"Dossier {self.id} - {self.user.username} - {self.vehicle}"
    

class Document(models.Model):
    """
    Model representing a document uploaded to a folder. Each document is associated with a specific folder and includes a file field for the uploaded document.
    """
    
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the base name of the uploaded file for display purposes.
        """

        return os.path.basename(self.file.name)