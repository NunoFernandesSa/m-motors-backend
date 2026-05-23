from rest_framework import serializers
from .models import Folder
from vehicles.serializers import VehicleSerializer
from users.serializers import UserSerializer


class FolderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Folder model, including nested serializers for related User and Vehicle.
    """
    
    user_details = UserSerializer(source='user', read_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'user', 'user_details', 'vehicle', 'vehicle_details', 'status', 'documents', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'comment']
        extra_kwargs = {
            'user': {'write_only': True},
            'vehicle': {'write_only': True},
        }


class FolderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Folder, allowing only the vehicle and documents fields to be set by the client.
    """

    class Meta:
        model = Folder
        fields = ['vehicle', 'documents']

    def validate_vehicle(self, value):
        """
        Ensure the selected vehicle is available for rental.
        """
        
        if not value.is_available:
            raise serializers.ValidationError("Ce véhicule n'est plus disponible.")
        return value
