from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle


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