import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from vehicles.models import (
    Vehicle,
    VehicleImage,
)

fake = Faker("fr_FR")

# Brands and models (realistic)
BRANDS_MODELS = {
    "Peugeot": ["208", "308", "508", "3008", "5008"],
    "Renault": ["Clio", "Megane", "Captur", "Arkana", "Scenic"],
    "Citroën": ["C3", "C4", "C5 Aircross", "Berlingo"],
    "BMW": ["Série 1", "Série 3", "Série 5", "X1", "X3"],
    "Audi": ["A3", "A4", "Q3", "Q5", "e-tron"],
    "Mercedes": ["Classe A", "Classe C", "GLA", "GLC"],
    "Volkswagen": ["Golf", "Polo", "T-Cross", "Tiguan"],
    "Ford": ["Fiesta", "Focus", "Kuga", "Mustang Mach-E"],
    "Tesla": ["Model 3", "Model Y", "Model S"],
    "Dacia": ["Sandero", "Duster", "Jogger"],
}

FUEL_TYPES = ["essence", "diesel", "electrique", "hybride"]
TRANSMISSIONS = ["manuel", "automatique"]
COLORS = [
    "Blanc",
    "Noir",
    "Rouge",
    "Bleu Océan",
    "Gris Tourmaline",
    "Argent",
    "Vert Émeraude",
    "Jaune",
]


class Command(BaseCommand):
    help = "Génère des véhicules factices pour le développement (adapté au modèle M-Motors)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Nombre de véhicules à générer (défaut: 50)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        self.stdout.write(f"🚗 Génération de {count} véhicules...")

        Vehicle.objects.all().delete()
        VehicleImage.objects.all().delete()

        for i in range(1, count + 1):
            brand = random.choice(list(BRANDS_MODELS.keys()))
            model = random.choice(BRANDS_MODELS[brand])

            is_sale = random.choice([True, False])

            vehicle = Vehicle.objects.create(
                ref=f"VEH-{str(i).zfill(4)}",  # Sera écrasé par la méthode save() mais c'est propre
                brand=brand,
                model=model,
                year=random.randint(2018, 2025),
                mileage=random.randint(0, 80000),
                fuel_type=random.choice(FUEL_TYPES),
                transmission=random.choice(TRANSMISSIONS),
                color=random.choice(COLORS),
                description=fake.paragraph(nb_sentences=3),
                vehicle_type=(
                    Vehicle.VehicleType.SALE if is_sale else Vehicle.VehicleType.RENT
                ),
                sale_price=round(random.uniform(10000, 45000), 2) if is_sale else None,
                rent_price=(
                    round(random.uniform(300, 1200), 2) if not is_sale else None
                ),
                rent_duration_min=(random.randint(1, 12) if not is_sale else None),  #
                is_available=random.choice([True, True, True, False]),
            )

            num_images = random.randint(1, 3)
            for order in range(1, num_images + 1):
                VehicleImage.objects.create(
                    vehicle=vehicle,
                    # Comme image est un ImageField nullable (blank=True, null=True),
                    # on laisse à None pour éviter des soucis de téléchargement vers S3/local.
                    # Si tu veux VRAIMENT une image, utilise un fichier local plus bas.
                    image=None,
                    order=order,
                )

            if i % 10 == 0:
                self.stdout.write(f"   ✅ {i} véhicules créés...")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Terminé ! {count} véhicules générés.")
        )
