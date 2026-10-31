from django.contrib import admin

from .models import Cocktail, CocktailIngredient, Ingredient


class CocktailIngredientInline(admin.TabularInline):
    model = CocktailIngredient
    extra = 1


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    search_fields = ["name", "category"]
    inlines = [CocktailIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "is_alcoholic"]
    list_filter = ["is_alcoholic"]
    search_fields = ["name"]
