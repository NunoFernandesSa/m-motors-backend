from rest_framework import viewsets
from users import models
from vehicles.models import Vehicle
from vehicles.permissions import CanManageVehicles, IsCommercialOrAdmin
from vehicles.serializers import VehicleCreateUpdateSerializer, VehicleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample


@extend_schema_view(
    list=extend_schema(
        summary="Liste des véhicules disponibles",
        description="Retourne la liste des véhicules avec possibilité de filtrage par type (sale/rent), marque, modèle, et fourchette de prix.",
        tags=["vehicles"],
        parameters=[
            OpenApiParameter(name="type", type=str, location=OpenApiParameter.QUERY, enum=["sale", "rent"], description="Type de contrat (vente ou location)"),
            OpenApiParameter(name="brand", type=str, location=OpenApiParameter.QUERY, description="Marque (recherche insensible à la casse)"),
            OpenApiParameter(name="model", type=str, location=OpenApiParameter.QUERY, description="Modèle (recherche insensible à la casse)"),
            OpenApiParameter(name="min_price", type=float, location=OpenApiParameter.QUERY, description="Prix minimum (selon le type)"),
            OpenApiParameter(name="max_price", type=float, location=OpenApiParameter.QUERY, description="Prix maximum"),
        ],
        responses={200: VehicleSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Exemple de filtre",
                value={ "type": "sale", "brand": "Renault", "min_price": 10000 },
                request_only=True,
            )
        ]
    ),
    create=extend_schema(
        summary="Ajouter un véhicule",
        description="Crée un nouveau véhicule. Réservé aux commerciaux/admins. Les champs `sale_price` ou `rent_price` sont obligatoires selon `vehicle_type`.",
        tags=["vehicles"],
        request=VehicleCreateUpdateSerializer,
        responses={
            201: VehicleSerializer,
            400: OpenApiResponse(description="Erreur de validation (prix manquant, année invalide, etc.)"),
            403: OpenApiResponse(description="Permission non accordée"),
        }
    ),
    retrieve=extend_schema(
        summary="Détail d'un véhicule",
        description="Retourne les informations complètes d'un véhicule spécifique.",
        tags=["vehicles"],
        responses={200: VehicleSerializer, 404: OpenApiResponse(description="Véhicule non trouvé")}
    ),
    update=extend_schema(
        summary="Modifier tout un véhicule",
        description="Remplace l'intégralité des données d'un véhicule. Réservé aux commerciaux/admins.",
        tags=["vehicles"],
        request=VehicleCreateUpdateSerializer,
        responses={200: VehicleSerializer}
    ),
    partial_update=extend_schema(
        summary="Modification partielle",
        description="Met à jour certains champs d'un véhicule. Réservé aux commerciaux/admins.",
        tags=["vehicles"],
        request=VehicleCreateUpdateSerializer,
        responses={200: VehicleSerializer}
    ),
    destroy=extend_schema(
        summary="Supprimer un véhicule",
        description="Supprime définitivement un véhicule. Réservé aux commerciaux/admins.",
        tags=["vehicles"],
        responses={204: OpenApiResponse(description="Supprimé avec succès"), 403: OpenApiResponse(description="Permission non accordée")}
    ),
    change_type=extend_schema(
        summary="Basculer entre vente et location",
        description="Change le type de contrat d'un véhicule. Nécessite la permission `can_change_vehicle_type`. Fournir les nouveaux prix selon le type.",
        tags=["vehicles"],
        methods=["PATCH"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "vehicle_type": {"type": "string", "enum": ["sale", "rent"]},
                    "sale_price": {"type": "number", "description": "Prix de vente (si passage à 'sale')"},
                    "rent_price": {"type": "number", "description": "Loyer mensuel (si passage à 'rent')"},
                    "rent_duration_min": {"type": "integer", "description": "Durée minimale en mois (si passage à 'rent')"}
                }
            }
        },
        responses={200: VehicleSerializer, 400: OpenApiResponse(description="Données invalides"), 403: OpenApiResponse(description="Permission non accordée")}
    )
)
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
