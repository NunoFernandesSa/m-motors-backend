from rest_framework import viewsets
from users import models
from vehicles.models import Vehicle
from vehicles.permissions import CanManageVehicles, IsCommercialOrAdmin
from vehicles.serializers import VehicleCreateUpdateSerializer, VehicleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for managing vehicles. Allows listing, creating, updating, and deleting vehicles.
    Also includes a custom action to change the type of a vehicle (sale/rent).
    """

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """
        Override the default permissions to allow only commercial users and admins to manage vehicles.
        Regular users can only view vehicles.
        """

        if self.action in ['create', 'update', 'partial_update', 'destroy', 'change_type']:
            permission_classes = [IsCommercialOrAdmin, CanManageVehicles]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Override the default serializer to use different serializers for different actions. For create and update actions, use VehicleCreateUpdateSerializer which includes validation for price fields. For other actions, use VehicleSerializer which includes a method field for price.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return VehicleCreateUpdateSerializer
        return VehicleSerializer
    
    def get_queryset(self):
        """
        Override the default queryset to allow filtering based on query parameters.
        Supported filters:
        - type: 'sale' or 'rent'
        - brand: filter by brand name (case-insensitive)
        - model: filter by model name (case-insensitive)
        - min_price: filter by minimum price
        - max_price: filter by maximum price
        """

        queryset = Vehicle.objects.filter(is_available=True)

        vehicle_type = self.request.query_params.get('type')
        if vehicle_type in ['sale', 'rent']:
            queryset = queryset.filter(vehicle_type=vehicle_type)

        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        model = self.request.query_params.get('model')
        if model:
            queryset = queryset.filter(model__icontains=model)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            if vehicle_type == 'sale':
                queryset = queryset.filter(sale_price__gte=min_price)
            elif vehicle_type == 'rent':
                queryset = queryset.filter(rent_price__gte=min_price)
            else:
                queryset = queryset.filter(
                    models.Q(vehicle_type='sale', sale_price__gte=min_price) |
                    models.Q(vehicle_type='rent', rent_price__gte=min_price)
                )

        max_price = self.request.query_params.get('max_price')
        if max_price:
            if vehicle_type == 'sale':
                queryset = queryset.filter(sale_price__lte=max_price)
            elif vehicle_type == 'rent':
                queryset = queryset.filter(rent_price__lte=max_price)
            else:
                queryset = queryset.filter(
                    models.Q(vehicle_type='sale', sale_price__lte=max_price) |
                    models.Q(vehicle_type='rent', rent_price__lte=max_price)
                )

        return queryset

    @action(detail=True, methods=['patch'])
    def change_type(self, request, pk=None):
        """
        Custom action to change the type of a vehicle (sale/rent).
        Only accessible to commercial users and admins.
        Needs permission 'vehicles.can_change_vehicle_type'
        """

        vehicle = self.get_object()

        if not request.user.has_perm('vehicles.can_change_vehicle_type'):
            return Response(
                {"detail": "Permission non accordée pour changer le type de véhicule."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_type = request.data.get('vehicle_type')
        if new_type not in ['sale', 'rent']:
            return Response({'error': 'Type de véhicule invalide. Doit être "vente" ou "location".'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_type == 'sale' and vehicle.vehicle_type == 'rent':
            vehicle.sale_price = request.data.get('sale_price', None)
            if not vehicle.sale_price:
                return Response({"detail": "Le prix de vente est requis."}, status=status.HTTP_400_BAD_REQUEST)
            vehicle.rent_price = None
            vehicle.rent_duration_min = None
        elif new_type == 'rent' and vehicle.vehicle_type == 'sale':
            vehicle.rent_price = request.data.get('rent_price', None)
            if not vehicle.rent_price:
                return Response({"detail": "Le loyer mensuel est requis."}, status=status.HTTP_400_BAD_REQUEST)
            vehicle.sale_price = None
            vehicle.rent_duration_min = request.data.get('rent_duration_min', 12)

        vehicle.vehicle_type = new_type
        vehicle.save()
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)  
