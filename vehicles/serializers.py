from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Vehicle model. It converts Vehicle instances to and from JSON format for API interactions. The serializer includes all fields of the Vehicle model, but marks 'created_at' and 'updated_at' as read-only to prevent them from being modified through API requests.
    """

    price = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'brand', 'model', 'year', 'mileage', 'fuel_type',
            'transmission', 'color', 'description', 'images', 'vehicle_type',
            'sale_price', 'rent_price', 'rent_duration_min', 'is_available',
            'created_at', 'updated_at', 'price'
        ]
        read_only_fields = ['created_at', 'updated_at']
      
        def get_price(self, obj):
          """
          Method to determine the price of the vehicle based on its type. If the vehicle is for sale, it returns the sale price; if it is for rent, it returns the rent price. This method allows the API to provide a single 'price' field that dynamically reflects the appropriate price based on the vehicle's type.
          """

          if obj.vehicle_type == 'sale':
              return obj.sale_price
          
          return obj.rent_price


class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Vehicle instances. This serializer is used when a new vehicle is being added to the system. It includes all fields of the Vehicle model except for 'created_at' and 'updated_at', which are automatically set by the system and should not be provided by the user.
    """
    class Meta:
        model = Vehicle
        fields = ['__all__']

    def validate(self, data):
        """
        Validation to ensure that the appropriate price field is provided based on the vehicle type. This method checks the 'vehicle_type' field and ensures that if the vehicle is for sale, a 'sale_price' is provided, and if the vehicle is for rent, a 'rent_price' is provided. It also sets the non-applicable price fields to None to maintain data integrity.
        """
        
        vehicle_type = data.get('vehicle_type')
        sale_price = data.get('sale_price')
        rent_price = data.get('rent_price')

        if vehicle_type == 'sale':
            if not sale_price:
                raise serializers.ValidationError(
                    {"sale_price": "Le prix de vente est requis pour un véhicule à vendre."}
                )
            data['rent_price'] = None
            data['rent_duration_min'] = None
        elif vehicle_type == 'rent':
            if not rent_price:
                raise serializers.ValidationError(
                    {"rent_price": "Le loyer mensuel est requis pour un véhicule en location."}
                )
            data['sale_price'] = None
        else:
            raise serializers.ValidationError({"vehicle_type": "Type invalide."})

        return data

    def validate_year(self, value):
        """
        Validation to ensure that the year of the vehicle is between 1990 and the current year plus one. This method checks if the provided year value is less than 1990 or greater than the current year plus one, and raises a validation error if it is, as vehicles outside this range are not considered valid for this application.
        """

        import datetime
        current_year = datetime.date.today().year
        if value < 1990 or value > current_year + 1:
            raise serializers.ValidationError(f"L'année doit être comprise entre 1990 et {current_year + 1}.")
        return value

    def validate_mileage(self, value):
        """
        Validation to ensure that the mileage is not negative. This method checks if the provided mileage value is less than zero and raises a validation error if it is, as mileage cannot be negative.
        """
        if value < 0:
            raise serializers.ValidationError("Le kilométrage ne peut pas être négatif.")
        return value
