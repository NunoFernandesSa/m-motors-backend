# folders/tests.py
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from vehicles.models import Vehicle
from folders.models import Folder, Document


class FolderAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Groupes
        cls.admin_group, _ = Group.objects.get_or_create(name='admin')
        cls.commercial_group, _ = Group.objects.get_or_create(name='commercial')
        cls.user_group, _ = Group.objects.get_or_create(name='user')
        
        # Récupérer la permission 'can_validate_folder' existante (créée par migration)
        content_type = ContentType.objects.get_for_model(Folder)
        try:
            perm = Permission.objects.get(codename='can_validate_folder', content_type=content_type)
        except Permission.DoesNotExist:
            # Si elle n'existe pas, on la crée (pour éviter l'erreur)
            perm = Permission.objects.create(
                codename='can_validate_folder',
                name='Can validate folder',
                content_type=content_type
            )
        cls.commercial_group.permissions.add(perm)
        # Ajouter aussi la permission 'can_view_all_folders' si nécessaire
        try:
            perm2 = Permission.objects.get(codename='can_view_all_folders', content_type=content_type)
        except Permission.DoesNotExist:
            perm2 = Permission.objects.create(
                codename='can_view_all_folders',
                name='Can view all folders',
                content_type=content_type
            )
        cls.commercial_group.permissions.add(perm2)
        
        # Utilisateurs
        cls.admin_user = User.objects.create_superuser(username="admin", password="adminpass")
        cls.admin_user.groups.add(cls.admin_group)
        cls.commercial_user = User.objects.create_user(username="commercial", password="commercialpass")
        cls.commercial_user.groups.add(cls.commercial_group)
        cls.regular_user = User.objects.create_user(username="client", password="clientpass")
        cls.regular_user.groups.add(cls.user_group)
        
        # Véhicule nécessaire
        cls.vehicle = Vehicle.objects.create(
            brand="Renault", model="Clio", year=2020, mileage=10000,
            fuel_type="essence", transmission="manuel", color="Rouge",
            description="Test", vehicle_type="sale", sale_price=15000,
            is_available=True
        )
        
    def test_create_folder_as_client(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {"vehicle": self.vehicle.id}
        response = self.client.post("/api/folders/", data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Folder.objects.count(), 1)
        folder = Folder.objects.first()
        self.assertEqual(folder.user, self.regular_user)
    
    def test_create_folder_unauthenticated(self):
        response = self.client.post("/api/folders/", {"vehicle": self.vehicle.id}, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_list_folders_as_client_own_only(self):
        # Créer deux dossiers pour le client
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        # Créer un dossier pour un autre utilisateur
        other_user = User.objects.create_user(username="other", password="other")
        Folder.objects.create(user=other_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/folders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_list_folders_as_commercial_sees_all(self):
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        Folder.objects.create(user=self.commercial_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.get("/api/folders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], folder.id)
    
    def test_retrieve_folder_other_user_forbidden(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        other = User.objects.create_user(username="other", password="other")
        self.client.force_authenticate(user=other)
        response = self.client.get(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 403)
    
    def test_update_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        data = {"comment": "Nouveau commentaire"}
        response = self.client.patch(f"/api/folders/{folder.id}/", data, format='json')
        self.assertEqual(response.status_code, 200)
        folder.refresh_from_db()
        self.assertEqual(folder.comment, "Nouveau commentaire")
    
    def test_delete_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Folder.objects.filter(id=folder.id).count(), 0)
    
    def test_validate_folder_as_commercial(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.patch(f"/api/folders/{folder.id}/validate/",
                                     {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, 200)
        folder.refresh_from_db()
        self.assertEqual(folder.status, "approved")
    
    def test_validate_folder_with_comment(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.patch(f"/api/folders/{folder.id}/validate/",
                                     {"status": "rejected", "comment": "Documents manquants"},
                                     format='json')
        self.assertEqual(response.status_code, 200)
        folder.refresh_from_db()
        self.assertEqual(folder.status, "rejected")
        self.assertEqual(folder.validation_comment, "Documents manquants")
    
    def test_validate_folder_as_regular_user_forbidden(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(f"/api/folders/{folder.id}/validate/",
                                     {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_upload_document_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        response = self.client.post(f"/api/folders/{folder.id}/documents/",
                                    {"file": file}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(folder.document_files.count(), 1)
    
    def test_upload_document_other_user_forbidden(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        other = User.objects.create_user(username="other", password="other")
        self.client.force_authenticate(user=other)
        file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        response = self.client.post(f"/api/folders/{folder.id}/documents/",
                                    {"file": file}, format='multipart')
        self.assertEqual(response.status_code, 403)
    
    def test_upload_document_commercial_allowed(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        response = self.client.post(f"/api/folders/{folder.id}/documents/",
                                    {"file": file}, format='multipart')
        self.assertEqual(response.status_code, 201)