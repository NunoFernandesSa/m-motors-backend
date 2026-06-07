from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Vehicle, VehicleImage


class VehicleImageSerializer(serializers.ModelSerializer):
    """Serializer for the VehicleImage model. It converts VehicleImage instances to and from JSON format for API interactions. The serializer includes the 'id', 'image', 'order', and 'created_at' fields, with 'id' and 'created_at' marked as read-only to prevent them from being modified through API requests.
    """
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vehicle model. It converts Vehicle instances to and from JSON format for API interactions. The serializer includes all fields of the Vehicle model, but marks 'created_at' and 'updated_at' as read-only to prevent them from being modified through API requests.
    """

    price = serializers.SerializerMethodField()
    images = VehicleImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Vehicle
        fields = [
            'id', 'ref', 'brand', 'model', 'year', 'mileage', 'fuel_type',
            'transmission', 'color', 'description', 'images', 'vehicle_type',
            'sale_price', 'rent_price', 'rent_duration_min', 'is_available',
            'created_at', 'updated_at', 'price', 'uploaded_images'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """Custom create method to handle the creation of a Vehicle instance along with its associated images. It first extracts the uploaded images from the validated data, creates the Vehicle instance, and then iterates over the uploaded images to create corresponding VehicleImage instances linked to the created Vehicle. This allows for a seamless creation process where both the vehicle and its images can be created in a single API request.
        """
        uploaded_images = validated_data.pop('uploaded_images', [])
        vehicle = Vehicle.objects.create(**validated_data)
        for idx, img in enumerate(uploaded_images):
            VehicleImage.objects.create(vehicle=vehicle, image=img, order=idx)
        return vehicle
    
    def update(self, instance, validated_data):
        """Custom update method to handle the updating of a Vehicle instance along with its associated images. It first extracts the uploaded images from the validated data, updates the Vehicle instance with the new data, and then checks if there are any uploaded images. If there are, it deletes all existing images associated with the vehicle and creates new VehicleImage instances for each of the uploaded images. This allows for a seamless update process where both the vehicle and its images can be updated in a single API request.
        """
        uploaded_images = validated_data.pop('uploaded_images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if uploaded_images is not None:
            instance.images.all().delete()
            for idx, img in enumerate(uploaded_images):
                VehicleImage.objects.create(vehicle=instance, image=img, order=idx)
        return instance
      
    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_price(self, obj):
        """
        Method to determine the price of the vehicle based on its type. If the vehicle is for sale, it returns the sale price; if it is for rent, it returns the rent price. This method allows the API to provide a single 'price' field that dynamically reflects the appropriate price based on the vehicle's type.
        """

        if obj.vehicle_type == 'sale':
            return obj.sale_price
        return obj.rent_price
