from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100)

    def __str__(self):
        return self.name_ru


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100)

    def __str__(self):
        return self.name_ru


class Cocktail(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    instruction = models.TextField()
    instruction_ru = models.TextField()
    is_alcoholic = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    external_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name_ru


class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, blank=True, null=True)
