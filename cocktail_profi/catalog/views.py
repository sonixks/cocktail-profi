import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from catalog.models import Category, Cocktail, Favourite


@login_required
def toggle_like_cocktail(request, cocktail_id):
    cocktail_obj = get_object_or_404(Cocktail, id=cocktail_id)
    favourite, created = Favourite.objects.get_or_create(
        user=request.user,
        cocktail=cocktail_obj
    )

    if not created:
        favourite.delete()
    return redirect(request.META.get('HTTP_REFERER', 'catalog:home'))


def get_published_cocktails():
    result = Cocktail.objects.select_related(
        'category',
        ).filter(
            is_published=True
        )
    return result


def get_random_cocktails(cocktails_list, cocktails_number):
    cocktails_list = list(cocktails_list)
    return random.sample(cocktails_list, cocktails_number)


def cocktails_list(request):
    template = 'catalog/cocktails_list.html'
    cocktails_list = get_published_cocktails()
    if request.GET:
        sub_string = request.GET.get('search_query')
        if sub_string is not None and not sub_string.strip():
            return redirect('catalog:home')
        cocktails = cocktails_list.filter(
            Q(name__icontains=sub_string) |
            Q(name_ru__icontains=sub_string) |
            Q(name_ru__icontains=sub_string.capitalize())
        )
    else:
        cocktails = get_random_cocktails(cocktails_list, 24)
    favorite_cocktails = []
    if request.user.is_authenticated:
        favorite_cocktails = request.user.favorites.values_list(
            'cocktail_id',
            flat=True
        )
    context = {
        'cocktails_list': cocktails,
        'favorite_cocktails': favorite_cocktails
    }
    return render(request, template, context)


def get_favotite_cocktails(request):
    favorite_cocktails = []
    if request.user.is_authenticated:
        favorite_cocktails = request.user.favorites.values_list(
            'cocktail_id',
            flat=True
        )
    return favorite_cocktails


def cocktail_detail(request, cocktail_id):
    template = 'catalog/cocktail_detail.html'
    cocktail = get_object_or_404(get_published_cocktails().filter(
        id=cocktail_id
    ))
    favorite_cocktails = get_favotite_cocktails(request)
    context = {
        'cocktail': cocktail,
        'favorite_cocktails': favorite_cocktails
    }
    return render(request, template, context)


def categories_list(request):
    template = 'catalog/categories_list.html'
    categories = Category.objects.all().order_by('name_ru')
    context = {
        'categories': categories
    }
    return render(request, template, context)


def cocktails_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    cocktails = get_published_cocktails().filter(
        category=category
    )
    template = 'catalog/cocktails_list.html'
    favorite_cocktails = get_favotite_cocktails(request)
    context = {
        'category': category,
        'cocktails_list': cocktails,
        'favorite_cocktails': favorite_cocktails
    }
    return render(request, template, context)


@login_required
def favorite_cocktails(request):
    template = 'catalog/cocktails_list.html'
    favorite_cocktails = get_favotite_cocktails(request)
    cocktails = get_published_cocktails().filter(
        id__in=favorite_cocktails
    )

    context = {
        'cocktails_list': cocktails,
        'favorite_cocktails': favorite_cocktails
    }
    return render(request, template, context)
