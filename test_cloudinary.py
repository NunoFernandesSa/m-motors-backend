import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.conf import settings

print("=== Cloudinary Configuration ===")
print(f"CLOUD_NAME: {settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')}")
print(f"API_KEY: {settings.CLOUDINARY_STORAGE.get('API_KEY')}")
print(f"API_SECRET: {'*' * len(settings.CLOUDINARY_STORAGE.get('API_SECRET', ''))}")
print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

if settings.DEFAULT_FILE_STORAGE == "cloudinary_storage.storage.MediaCloudinaryStorage":
    print("\n✅ Cloudinary storage is configured correctly!")
else:
    print("\n❌ Cloudinary storage NOT configured! Check your environment variables!")
