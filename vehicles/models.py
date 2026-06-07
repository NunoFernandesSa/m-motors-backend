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

    ref = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Référence")
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
    
    # images = models.JSONField(default=list, verbose_name="Images", help_text="Liste d'URLs d'images")
    
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

    def save(self, *args, **kwargs):
        if not self.ref:
            prefix = f"{self.year}-{self.brand.upper()}"
            last = Vehicle.objects.filter(ref__startswith=prefix).order_by('id').last()
            if last:
                try:
                    last_num = int(last.ref.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.ref = f"{prefix}-{new_num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.get_vehicle_type_display()}"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicles/%Y/%m/',blank=True, null=True, verbose_name="Images")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return f"Image {self.id} - {self.vehicle}"