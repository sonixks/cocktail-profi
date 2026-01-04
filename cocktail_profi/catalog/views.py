import random

from django.shortcuts import get_object_or_404, render

from catalog.models import Category, Cocktail


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
    cocktails = get_random_cocktails(cocktails_list, 24)
    context = {
        'cocktails_list': cocktails
    }
    return render(request, template, context)


def cocktail_detail(request, cocktail_id):
    template = 'catalog/cocktail_detail.html'
    cocktail = get_object_or_404(get_published_cocktails().filter(
        id=cocktail_id
    ))
    context = {
        'cocktail': cocktail
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
    context = {
        'category': category,
        'cocktails_list': cocktails,
    }
    return render(request, template, context)
