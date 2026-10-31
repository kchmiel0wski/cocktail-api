from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_alcoholic = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Cocktail(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="CocktailIngredient",
        related_name="cocktails",
    )

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="cocktail_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="cocktail_ingredients",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    unit = models.CharField(max_length=30)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["cocktail", "ingredient"],
                name="unique_ingredient_per_cocktail",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="cocktail_ingredient_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient}"
