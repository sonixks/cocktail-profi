from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from bar.models import UserStock
from catalog.models import Ingredient


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
            Q(name_ru__icontains=sub_string)
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
