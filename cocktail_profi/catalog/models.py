from django.db import models


class MeasurementUnit(models.Model):
    name_en = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Ед. изм. (EN)"
    )
    name_ru = models.CharField(max_length=50, verbose_name="Ед. изм. (RU)")

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return f"{self.name_en} -> {self.name_ru}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ('-id',)
        verbose_name = 'коктейль'
        verbose_name_plural = 'Коктейли'

    def __str__(self):
        return self.name


class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, blank=True, null=True)
