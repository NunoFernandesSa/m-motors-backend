from django.db import models


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        SALE = 'sale', 'Vente'
        RENT = 'rent', 'Location'

    class FuelType(models.TextChoices):
        GASOLINE = 'essence', 'Essence'
        DIESEL = 'diesel', 'Diesel'
        ELECTRIC = 'electrique', 'Électrique'
        HYBRID = 'hybride', 'Hybride'

    class Transmission(models.TextChoices):
        MANUAL = 'manuel', 'Manuelle'
        AUTOMATIC = 'automatique', 'Automatique'

    brand = models.CharField(max_length=100, verbose_name="Marque")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    year = models.IntegerField(verbose_name="Année")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente", null=True, blank=True)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Loyer mensuel", null=True, blank=True)
    mileage = models.IntegerField(verbose_name="Kilométrage")
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, verbose_name="Type de carburant")
    transmission = models.CharField(max_length=20, choices=Transmission.choices, verbose_name="Boîte de vitesses")
    color = models.CharField(max_length=50, verbose_name="Couleur")
    description = models.TextField(verbose_name="Description")
    rent_duration_min = models.PositiveIntegerField(null=True, blank=True, help_text="Durée minimale de location en mois")
    
    # Images (stockage en JSON pour dev, à migrer vers S3 plus tard)
    # TODO : Migrer vers un système de stockage d'images (ex: S3) et utiliser un champ ImageField ou un modèle séparé pour les images
    images = models.JSONField(default=list, verbose_name="Images", help_text="Liste d'URLs d'images")
    
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, verbose_name="Type de véhicule")
    
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
   
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['-created_at']
        permissions = [
            ("can_manage_vehicles", "Peut gérer tous les véhicules (CRUD)"),
            ("can_change_vehicle_type", "Peut basculer un véhicule de vente à location et inversement"),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.get_vehicle_type_display()}"
