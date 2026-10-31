from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.viewsets import ModelViewSet

from .models import Cocktail, Ingredient
from .pagination import ValidatedPageNumberPagination
from .serializers import (
    CocktailFilterSerializer,
    CocktailSerializer,
    IngredientFilterSerializer,
    IngredientSerializer,
)


class IngredientInUse(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Remove this ingredient from its cocktails before deleting it."
    default_code = "ingredient_in_use"


class FilteredPaginatedModelViewSet(ModelViewSet):
    pagination_class = ValidatedPageNumberPagination
    filter_serializer_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = self.filter_serializer_class(
            data=self.request.query_params.dict()
        )
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        if "name" in filters:
            queryset = queryset.filter(name__icontains=filters["name"])
        if "category" in filters:
            queryset = queryset.filter(category__iexact=filters["category"])
        if "is_alcoholic" in filters:
            queryset = queryset.filter(is_alcoholic=filters["is_alcoholic"])
        return queryset


class CocktailViewSet(FilteredPaginatedModelViewSet):
    queryset = Cocktail.objects.prefetch_related("cocktail_ingredients__ingredient")
    serializer_class = CocktailSerializer
    filter_serializer_class = CocktailFilterSerializer


class IngredientViewSet(FilteredPaginatedModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_serializer_class = IngredientFilterSerializer

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as error:
            raise IngredientInUse from error
