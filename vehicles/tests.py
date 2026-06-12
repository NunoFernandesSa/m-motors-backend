from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status

from vehicles.models import Vehicle, VehicleImage
from vehicles.serializers import VehicleSerializer


class VehicleModelTest(TestCase):
    """
    Unit tests for the Vehicle model and serializer.
      - Verify creation of a vehicle for sale
      - Verify creation of a vehicle for rent
      - Verify the model __str__ method
      - Verify serializer validation
    """
    @classmethod
    def setUpTestData(cls):
        Group.objects.get_or_create(name='admin')
        Group.objects.get_or_create(name='commercial')
        Group.objects.get_or_create(name='user')

    def test_create_vehicle_sale(self):
        vehicle = Vehicle.objects.create(
            brand="Renault", model="Clio", year=2023, mileage=10000,
            fuel_type="essence", transmission="manuel", color="Rouge",
            description="Test vente", vehicle_type="sale",
            sale_price=15000.00, is_available=True
        )
        self.assertEqual(vehicle.brand, "Renault")
        self.assertEqual(vehicle.vehicle_type, "sale")
        self.assertEqual(vehicle.sale_price, 15000.00)
        self.assertIsNotNone(vehicle.ref)

    def test_create_vehicle_rent(self):
        vehicle = Vehicle.objects.create(
            brand="Peugeot", model="208", year=2022, mileage=20000,
            fuel_type="diesel", transmission="automatique", color="Bleu",
            description="Test location", vehicle_type="rent",
            rent_price=350.00, rent_duration_min=24, is_available=True
        )
        self.assertEqual(vehicle.vehicle_type, "rent")
        self.assertEqual(vehicle.rent_price, 350.00)

    def test_vehicle_str(self):
        vehicle = Vehicle.objects.create(
            brand="Citroen", model="C3", year=2021, mileage=50000,
            fuel_type="essence", transmission="manuel", color="Blanc",
            description="", vehicle_type="sale", sale_price=12000.00
        )
        expected = f"{vehicle.brand} {vehicle.model} ({vehicle.year}) - Vente"
        self.assertEqual(str(vehicle), expected)


class VehicleSerializerTest(TestCase):
    """
    Unit tests for the VehicleSerializer to ensure correct validation and object creation.
    """

    def setUp(self):
        self.vehicle_data = {
            "brand": "Ford", "model": "Focus", "year": 2021, "mileage": 40000,
            "fuel_type": "diesel", "transmission": "automatique", "color": "Gris",
            "description": "Bon état", "vehicle_type": "sale", "sale_price": "18000.00"
        }

    def test_serializer_valid(self):
        serializer = VehicleSerializer(data=self.vehicle_data)
        self.assertTrue(serializer.is_valid())
        vehicle = serializer.save()
        self.assertEqual(vehicle.brand, "Ford")

    def test_serializer_missing_required(self):
        data = self.vehicle_data.copy()
        del data["brand"]
        serializer = VehicleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("brand", serializer.errors)


class VehicleAPITest(APITestCase):
    """
    Integration tests for the Vehicle API.
    """
    @classmethod
    def setUpTestData(cls):
        cls.admin_group, _ = Group.objects.get_or_create(name='admin')
        cls.commercial_group, _ = Group.objects.get_or_create(name='commercial')
        cls.user_group, _ = Group.objects.get_or_create(name='user')

        content_type = ContentType.objects.get_for_model(Vehicle)
        perm = Permission.objects.get(
            codename='can_manage_vehicles',
            content_type=content_type
        )
        cls.commercial_group.permissions.add(perm)

        cls.admin_user = User.objects.create_superuser(username="admin", password="adminpass")
        cls.admin_user.groups.add(cls.admin_group)
        cls.commercial_user = User.objects.create_user(username="commercial", password="commercialpass")
        cls.commercial_user.groups.add(cls.commercial_group)
        cls.regular_user = User.objects.create_user(username="user", password="userpass")
        cls.regular_user.groups.add(cls.user_group)

        cls.vehicle1 = Vehicle.objects.create(
            brand="BMW", model="Serie 1", year=2020, mileage=50000,
            fuel_type="essence", transmission="automatique", color="Noir",
            description="Voiture de test", vehicle_type="sale", sale_price=25000
        )
        cls.vehicle2 = Vehicle.objects.create(
            brand="Audi", model="A3", year=2021, mileage=30000,
            fuel_type="diesel", transmission="manuel", color="Gris",
            description="Voiture de test", vehicle_type="rent", rent_price=400, rent_duration_min=12
        )

    def test_list_vehicles_public(self):
        response = self.client.get("/api/vehicles/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_vehicle_type(self):
        response = self.client.get("/api/vehicles/?vehicle_type=rent")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vehicle_type'], 'rent')

    def test_filter_by_brand(self):
        response = self.client.get("/api/vehicles/?brand=BMW")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['brand'], 'BMW')

    def test_retrieve_vehicle_detail_public(self):
        response = self.client.get(f"/api/vehicles/{self.vehicle1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['brand'], 'BMW')

    def test_create_vehicle_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": "Tesla", "model": "Model 3", "year": 2023, "mileage": 0,
            "fuel_type": "electrique", "transmission": "automatique", "color": "Blanc",
            "description": "Neuf", "vehicle_type": "sale", "sale_price": "45000.00"
        }
        response = self.client.post("/api/vehicles/", data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_vehicle_as_commercial(self):
        self.client.force_authenticate(user=self.commercial_user)
        data = {
            "brand": "Renault", "model": "Zoe", "year": 2022, "mileage": 5000,
            "fuel_type": "electrique", "transmission": "automatique", "color": "Bleu",
            "description": "Voiture électrique",  # ← description obligatoire non vide
            "vehicle_type": "rent", "rent_price": 320.00,
            "rent_duration_min": 24
        }
        response = self.client.post("/api/vehicles/", data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_vehicle_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "brand": "Dacia", "model": "Sandero", "year": 2023, "mileage": 10,
            "fuel_type": "essence", "transmission": "manuel", "color": "Gris",
            "description": "Petite voiture", "vehicle_type": "sale", "sale_price": "12000"
        }
        response = self.client.post("/api/vehicles/", data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_update_vehicle_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f"/api/vehicles/{self.vehicle1.id}/", {"color": "Bleu"}, format='json')
        self.assertEqual(response.status_code, 200)
        self.vehicle1.refresh_from_db()
        self.assertEqual(self.vehicle1.color, "Bleu")

    def test_update_vehicle_as_commercial(self):
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.patch(f"/api/vehicles/{self.vehicle2.id}/", {"mileage": 28000}, format='json')
        self.assertEqual(response.status_code, 200)
        self.vehicle2.refresh_from_db()
        self.assertEqual(self.vehicle2.mileage, 28000)

    def test_update_vehicle_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(f"/api/vehicles/{self.vehicle1.id}/", {"color": "Vert"}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_vehicle_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/api/vehicles/{self.vehicle1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Vehicle.objects.filter(id=self.vehicle1.id).count(), 0)

    def test_delete_vehicle_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f"/api/vehicles/{self.vehicle2.id}/")
        self.assertEqual(response.status_code, 403)