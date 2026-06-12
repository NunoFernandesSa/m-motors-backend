from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from vehicles.models import Vehicle
from folders.models import Folder


class FolderAPITest(APITestCase):
    """Tests for Folder API endpoints, covering creation, retrieval, update, deletion, validation, and document upload,
    with different user roles (client, commercial, admin) and permissions.

    Permissions:
      - Clients can create folders, view their own folders, and update/delete their own folders.
      - Commercial users can view all folders, validate folders, and upload documents to any folder.
      - Admin users have all permissions of commercial users and can also manage users and groups.
    """
    @classmethod
    def setUpTestData(cls):
        # Groups
        cls.admin_group, _ = Group.objects.get_or_create(name='admin')
        cls.commercial_group, _ = Group.objects.get_or_create(name='commercial')
        cls.user_group, _ = Group.objects.get_or_create(name='user')

        # Retrieve existing permissions or create them if they don't exist
        content_type = ContentType.objects.get_for_model(Folder)
        perm_validate = Permission.objects.get_or_create(
            codename='can_validate_folder',
            content_type=content_type,
            defaults={'name': 'Can validate folder'}
        )[0]
        perm_view_all = Permission.objects.get_or_create(
            codename='can_view_all_folders',
            content_type=content_type,
            defaults={'name': 'Can view all folders'}
        )[0]
        cls.commercial_group.permissions.add(perm_validate, perm_view_all)
        cls.admin_group.permissions.add(perm_validate, perm_view_all)

        # Users
        cls.admin_user = User.objects.create_superuser(username="admin", password="adminpass")
        cls.admin_user.groups.add(cls.admin_group)
        cls.commercial_user = User.objects.create_user(username="commercial", password="commercialpass")
        cls.commercial_user.groups.add(cls.commercial_group)
        cls.regular_user = User.objects.create_user(username="client", password="clientpass")
        cls.regular_user.groups.add(cls.user_group)

        # Vehicles
        cls.vehicle = Vehicle.objects.create(
            brand="Renault", model="Clio", year=2020, mileage=10000,
            fuel_type="essence", transmission="manuel", color="Rouge",
            description="Test", vehicle_type="sale", sale_price=15000,
            is_available=True
        )

    def test_create_folder_as_client(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/api/folders/", {"vehicle": self.vehicle.id}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_list_folders_as_client_own_only(self):
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/folders/")
        self.assertEqual(len(response.data), 2)

    def test_list_folders_as_commercial_sees_all(self):
        Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        Folder.objects.create(user=self.commercial_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.get("/api/folders/")
        self.assertEqual(len(response.data), 2)

    def test_retrieve_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_folder_other_user_forbidden(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)  # commercial a accès à tout, donc on utilise autre user
        response = self.client.get(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 200)  # commercial autorisé
        # Test avec un user lambda
        other = User.objects.create_user(username="other", password="other")
        self.client.force_authenticate(user=other)
        response = self.client.get(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 403)

    def test_update_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(f"/api/folders/{folder.id}/", {"comment": "Nouveau"}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_folder_owner(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f"/api/folders/{folder.id}/")
        self.assertEqual(response.status_code, 204)

    def test_validate_folder_as_commercial(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.patch(f"/api/folders/{folder.id}/validate/",
                                     {"status": "approved"}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_validate_folder_with_comment(self):
        folder = Folder.objects.create(user=self.regular_user, vehicle=self.vehicle)
        self.client.force_authenticate(user=self.commercial_user)
        response = self.client.patch(f"/api/folders/{folder.id}/validate/",
                                     {"status": "rejected", "comment": "Manque document"}, format='json')
        self.assertEqual(response.status_code, 200)
        folder.refresh_from_db()
        self.assertEqual(folder.validation_comment, "Manque document")

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
