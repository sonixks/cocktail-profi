from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from bar.models import UserStock
from catalog.models import Cocktail, Ingredient


@login_required
def my_bar_view(request):
    template = 'bar/index.html'
    user_stock = UserStock.objects.filter(
        user=request.user
    ).select_related('ingredient').order_by('-id')
    sub_string = request.GET.get('query')
    result = []
    if sub_string:
        result = Ingredient.objects.filter(
            Q(name__icontains=sub_string) |
            Q(name_ru__icontains=sub_string) |
            Q(name_ru__icontains=sub_string.capitalize())
        )
    context = {
        'user_stock': user_stock,
        'result': result,
        'sub_string': sub_string or ''
    }
    return render(request, template, context)


@login_required
def add_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    UserStock.objects.get_or_create(
        user=request.user,
        ingredient=ingredient
    )
    return redirect('bar:index')


@login_required
def remove_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    UserStock.objects.filter(
        user=request.user,
        ingredient=ingredient
    ).delete()
    return redirect('bar:index')


@login_required
def cocktail_match_view(request):
    user_stock_names = set(
        UserStock.objects.filter(user=request.user)
        .values_list('ingredient__name', flat=True)
    )
    user_items = {name.lower().strip() for name in user_stock_names}

    if not user_items:
        return render(
            request,
            'bar/match.html',
            {'matches': [], 'almost_matches': []}
        )

    all_cocktails = Cocktail.objects.filter(
        is_published=True
    ).prefetch_related('cocktailingredient_set__ingredient')
    matches = []
    almost_matches = []

    for cocktail in all_cocktails:
        recipe_items = {
            ci.ingredient.name.lower().strip()

            for ci in cocktail.cocktailingredient_set.all()
        }
        if not recipe_items:
            continue
        missing_count = 0
        found_count = 0

        for recipe_ing in recipe_items:
            is_found = False

            for user_ing in user_items:
                if recipe_ing == user_ing or recipe_ing in user_ing or user_ing in recipe_ing:
                    is_found = True
                    break

            if is_found:
                found_count += 1
            else:
                missing_count += 1
        if missing_count == 0:
            matches.append(cocktail)
        elif missing_count <= 2 and found_count > 0: 
            almost_matches.append(cocktail)

    context = {
        'matches': matches,
        'almost_matches': almost_matches,
    }
    return render(request, 'bar/match.html', context)
