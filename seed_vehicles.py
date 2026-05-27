import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from vehicles.models import Vehicle

vehicles_data = [
    # Ventes (vehicle_type='sale')
    {
        "brand": "Renault",
        "model": "Clio",
        "year": 2020,
        "mileage": 25000,
        "fuel_type": "essence",
        "transmission": "manuelle",
        "color": "Rouge",
        "description": "Très bonne état, révisée.",
        "vehicle_type": "sale",
        "sale_price": "12500",
        "rent_price": None,
        "rent_duration_min": None,
        "is_available": True,
        "images": "https://picsum.photos/id/100/400/300",
    },
    {
        "brand": "Peugeot",
        "model": "208",
        "year": 2021,
        "mileage": 18000,
        "fuel_type": "diesel",
        "transmission": "automatique",
        "color": "Bleu",
        "description": "Clim, GPS, cuir.",
        "vehicle_type": "sale",
        "sale_price": "15800",
        "rent_price": None,
        "rent_duration_min": None,
        "is_available": True,
        "images": "https://picsum.photos/id/101/400/300",
    },
    {
        "brand": "Citroën",
        "model": "C3",
        "year": 2019,
        "mileage": 34000,
        "fuel_type": "essence",
        "transmission": "manuelle",
        "color": "Blanc",
        "description": "Intérieur spacieux.",
        "vehicle_type": "sale",
        "sale_price": "9900",
        "rent_price": None,
        "rent_duration_min": None,
        "is_available": True,
        "images": "https://picsum.photos/id/102/400/300",
    },
    # Locations (vehicle_type='rent')
    {
        "brand": "Tesla",
        "model": "Model 3",
        "year": 2022,
        "mileage": 5000,
        "fuel_type": "électrique",
        "transmission": "automatique",
        "color": "Noir",
        "description": "Location longue durée, entretien inclus.",
        "vehicle_type": "rent",
        "sale_price": None,
        "rent_price": "599",
        "rent_duration_min": 12,
        "is_available": True,
        "images": "https://picsum.photos/id/103/400/300",
    },
    {
        "brand": "Volkswagen",
        "model": "Golf",
        "year": 2021,
        "mileage": 22000,
        "fuel_type": "diesel",
        "transmission": "automatique",
        "color": "Gris",
        "description": "LLD 24 mois, assistance incluse.",
        "vehicle_type": "rent",
        "sale_price": None,
        "rent_price": "449",
        "rent_duration_min": 24,
        "is_available": True,
        "images": "https://picsum.photos/id/104/400/300",
    },
    {
        "brand": "BMW",
        "model": "Série 1",
        "year": 2023,
        "mileage": 1000,
        "fuel_type": "essence",
        "transmission": "automatique",
        "color": "Bleu foncé",
        "description": "Location avec option d'achat.",
        "vehicle_type": "rent",
        "sale_price": None,
        "rent_price": "699",
        "rent_duration_min": 36,
        "is_available": True,
        "images": "https://picsum.photos/id/105/400/300",
    },
]

# Insertion
for v in vehicles_data:
    obj, created = Vehicle.objects.get_or_create(
        brand=v["brand"],
        model=v["model"],
        year=v["year"],
        defaults=v,
    )
    if created:
        print(f"Ajouté : {v['brand']} {v['model']}")
    else:
        print(f"Déjà existant : {v['brand']} {v['model']}")

print("Seeding terminé.")
