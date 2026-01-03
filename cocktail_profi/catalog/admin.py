from django.contrib import admin

from catalog.models import Category, Cocktail, Ingredient, MeasurementUnit


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'name_ru',
    ]

    list_editable = [
        'name_ru',
    ]


class CocktailAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'name_ru',
        'category',
        'is_published'
    ]

    list_editable = [
        'name_ru',
        'category',
        'is_published'
    ]


class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'name_ru'
    ]

    list_editable = [
        'name_ru',
    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Cocktail, CocktailAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(MeasurementUnit)
