from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vehicle model. It converts Vehicle instances to and from JSON format for API interactions. The serializer includes all fields of the Vehicle model, but marks 'created_at' and 'updated_at' as read-only to prevent them from being modified through API requests.
    """
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Vehicle instances. This serializer is used when a new vehicle is being added to the system. It includes all fields of the Vehicle model except for 'created_at' and 'updated_at', which are automatically set by the system and should not be provided by the user.
    """
    class Meta:
        model = Vehicle
        fields = ['__all__']

    def validate_year(self, value):
        """
        Validation to ensure that the year of the vehicle is between 1990 and the current year plus one. This method checks if the provided year value is less than 1990 or greater than the current year plus one, and raises a validation error if it is, as vehicles outside this range are not considered valid for this application.
        """
        import datetime
        current_year = datetime.date.today().year
        if value < 1990 or value > current_year + 1:
            raise serializers.ValidationError(f"L'année doit être comprise entre 1990 et {current_year + 1}.")
        return value

    def validate_price(self, value):
        """
        Validation to ensure that the price is greater than zero. This method checks if the provided price value is less than or equal to zero and raises a validation error if it is, as a vehicle cannot have a non-positive price.
        """
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à zéro.")
        return value

    def validate_mileage(self, value):
        """
        Validation to ensure that the mileage is not negative. This method checks if the provided mileage value is less than zero and raises a validation error if it is, as mileage cannot be negative.
        """
        if value < 0:
            raise serializers.ValidationError("Le kilométrage ne peut pas être négatif.")
        return value

    def validate_rent_price_and_sale_price(self, attrs):
        """
        Custom validation to ensure that the sale price is greater than the rent price if both are provided.
        """        
        if attrs['sale_price'] and attrs['rent_price'] and attrs['sale_price'] <= attrs['rent_price']:
            raise serializers.ValidationError("Le prix de vente doit être supérieur au prix de location.")
        return attrs
    
    def validate_rent_duration_min(self, value):
        """
        Validation to ensure that the minimum rental duration is a positive integer. This method checks if the provided rent_duration_min value is less than or equal to zero and raises a validation error if it is, as a rental duration must be a positive integer.
        """

        if value is not None and value <= 0:
            raise serializers.ValidationError("La durée minimale de location doit être un entier positif.")
        
        return value
