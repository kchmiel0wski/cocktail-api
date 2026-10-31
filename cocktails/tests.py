from rest_framework.test import APITestCase

from .models import Cocktail, Ingredient


class IngredientApiTests(APITestCase):
    def test_ingredient_crud_and_filters(self):
        create_response = self.client.post(
            "/api/ingredients/",
            {
                "name": "Lime",
                "description": "Fresh lime",
                "is_alcoholic": False,
                "image_url": "https://example.com/lime.jpg",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        ingredient_id = create_response.data["id"]

        list_response = self.client.get("/api/ingredients/?name=lim&is_alcoholic=false")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data["count"], 1)

        detail_response = self.client.get(f"/api/ingredients/{ingredient_id}/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data["name"], "Lime")

        update_response = self.client.patch(
            f"/api/ingredients/{ingredient_id}/",
            {"description": "Juicy lime"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["description"], "Juicy lime")

        delete_response = self.client.delete(f"/api/ingredients/{ingredient_id}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Ingredient.objects.filter(pk=ingredient_id).exists())

    def test_ingredient_filter_and_pagination_parameters_are_validated(self):
        for index in range(3):
            Ingredient.objects.create(
                name=f"Ingredient {index}",
                is_alcoholic=index % 2 == 0,
            )

        self.assertEqual(
            self.client.get("/api/ingredients/?is_alcoholic=sometimes").status_code,
            400,
        )
        self.assertEqual(
            self.client.get("/api/ingredients/?page_size=101").status_code,
            400,
        )
        self.assertEqual(
            self.client.get("/api/ingredients/?unknown=value").status_code,
            400,
        )

        response = self.client.get("/api/ingredients/?page=1&page_size=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3, response.data)
        self.assertEqual(len(response.data["results"]), 2)


class CocktailApiTests(APITestCase):
    def setUp(self):
        self.lime = Ingredient.objects.create(name="Lime")
        self.rum = Ingredient.objects.create(name="Rum", is_alcoholic=True)

    def cocktail_payload(self):
        return {
            "name": "Mojito",
            "category": "Classic",
            "instructions": "Muddle, add ice, and stir.",
            "ingredients": [
                {"ingredient_id": self.lime.pk, "amount": "20.000", "unit": "ml"},
                {"ingredient_id": self.rum.pk, "amount": "50.000", "unit": "ml"},
            ],
        }

    def test_cocktail_crud_with_ingredient_amounts(self):
        create_response = self.client.post(
            "/api/cocktails/",
            self.cocktail_payload(),
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        cocktail_id = create_response.data["id"]
        self.assertEqual(len(create_response.data["ingredients"]), 2)
        self.assertEqual(
            create_response.data["ingredients"][0]["ingredient"]["name"],
            "Lime",
        )

        filtered_response = self.client.get("/api/cocktails/?category=classic")
        self.assertEqual(filtered_response.status_code, 200)
        self.assertEqual(filtered_response.data["count"], 1)

        detail_response = self.client.get(f"/api/cocktails/{cocktail_id}/")
        self.assertEqual(detail_response.status_code, 200)

        update_response = self.client.patch(
            f"/api/cocktails/{cocktail_id}/",
            {"name": "Virgin Mojito"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["name"], "Virgin Mojito")
        self.assertEqual(len(update_response.data["ingredients"]), 2)

        replacement_payload = {
            "name": "Lime drink",
            "category": "Non-alcoholic",
            "instructions": "Mix the ingredients.",
            "ingredients": [
                {"ingredient_id": self.lime.pk, "amount": "100", "unit": "ml"},
            ],
        }
        replace_response = self.client.put(
            f"/api/cocktails/{cocktail_id}/",
            replacement_payload,
            format="json",
        )
        self.assertEqual(replace_response.status_code, 200)
        self.assertEqual(len(replace_response.data["ingredients"]), 1)

        delete_response = self.client.delete(f"/api/cocktails/{cocktail_id}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Cocktail.objects.filter(pk=cocktail_id).exists())

    def test_cocktail_input_validation(self):
        payload = self.cocktail_payload()
        payload["ingredients"] = [
            {"ingredient_id": self.lime.pk, "amount": "0", "unit": "ml"}
        ]
        self.assertEqual(
            self.client.post("/api/cocktails/", payload, format="json").status_code,
            400,
        )

        payload = self.cocktail_payload()
        payload["ingredients"].append(payload["ingredients"][0])
        self.assertEqual(
            self.client.post("/api/cocktails/", payload, format="json").status_code,
            400,
        )

        payload = self.cocktail_payload()
        payload["ingredients"][0]["ingredient_id"] = 9999
        self.assertEqual(
            self.client.post("/api/cocktails/", payload, format="json").status_code,
            400,
        )

        self.assertEqual(
            self.client.get("/api/cocktails/?page=zero").status_code,
            400,
        )

    def test_used_ingredient_cannot_be_deleted_until_removed_from_cocktail(self):
        create_response = self.client.post(
            "/api/cocktails/",
            self.cocktail_payload(),
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)

        blocked_delete = self.client.delete(f"/api/ingredients/{self.lime.pk}/")
        self.assertEqual(blocked_delete.status_code, 409)
        self.assertTrue(Ingredient.objects.filter(pk=self.lime.pk).exists())

        self.client.delete(f"/api/cocktails/{create_response.data['id']}/")
        allowed_delete = self.client.delete(f"/api/ingredients/{self.lime.pk}/")
        self.assertEqual(allowed_delete.status_code, 204)
