from rest_framework import serializers
from django.db import transaction

from .models import Cocktail, CocktailIngredient, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "description", "is_alcoholic", "image_url"]
        read_only_fields = ["id"]


class CocktailIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient",
        write_only=True,
    )

    class Meta:
        model = CocktailIngredient
        fields = ["ingredient", "ingredient_id", "amount", "unit"]


class CocktailSerializer(serializers.ModelSerializer):
    ingredients = CocktailIngredientSerializer(
        source="cocktail_ingredients",
        many=True,
    )

    class Meta:
        model = Cocktail
        fields = ["id", "name", "category", "instructions", "ingredients"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if "cocktail_ingredients" in attrs:
            rows = attrs["cocktail_ingredients"]
            if not rows:
                raise serializers.ValidationError(
                    {"ingredients": "At least one ingredient is required."}
                )

            ingredient_ids = [row["ingredient"].pk for row in rows]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    {"ingredients": "An ingredient can only be listed once."}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ingredient_rows = validated_data.pop("cocktail_ingredients")
        cocktail = Cocktail.objects.create(**validated_data)
        CocktailIngredient.objects.bulk_create(
            [
                CocktailIngredient(cocktail=cocktail, **row)
                for row in ingredient_rows
            ]
        )
        return cocktail

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient_rows = validated_data.pop("cocktail_ingredients", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if ingredient_rows is not None:
            instance.cocktail_ingredients.all().delete()
            CocktailIngredient.objects.bulk_create(
                [
                    CocktailIngredient(cocktail=instance, **row)
                    for row in ingredient_rows
                ]
            )
        return instance


class StrictQuerySerializer(serializers.Serializer):
    def validate(self, attrs):
        allowed = set(self.fields) | {"page", "page_size"}
        unknown = set(self.initial_data) - allowed
        if unknown:
            raise serializers.ValidationError(
                {"query": f"Unknown query parameter(s): {', '.join(sorted(unknown))}."}
            )
        return attrs


class CocktailFilterSerializer(StrictQuerySerializer):
    name = serializers.CharField(required=False, max_length=120)
    category = serializers.CharField(required=False, max_length=80)


class IngredientFilterSerializer(StrictQuerySerializer):
    name = serializers.CharField(required=False, max_length=100)
    is_alcoholic = serializers.BooleanField(required=False)


class PaginationQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
