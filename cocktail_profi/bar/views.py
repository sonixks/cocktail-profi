from django.shortcuts import render

from catalog.models import Category, Cocktail, CocktailIngredient


def coctails_list(request):
    template = 'catalog/coctails_list.html'
    coctails_list = Cocktail.objects.select_related(
        Category, CocktailIngredient
        ).filter(
            is_published=True,

        ).order_by('-id')[:5]
    context = {
        'coctails_list': coctails_list
    }
    return render(request, template, context)
