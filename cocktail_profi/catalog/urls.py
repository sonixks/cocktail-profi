from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path('', views.cocktails_list, name='home'),
    path(
        'cocktail/<int:cocktail_id>/',
        views.cocktail_detail,
        name='cocktail_detail'
    ),
    path('category/', views.categories_list, name='categories_list'),
    path(
        'category/<int:category_id>/',
        views.cocktails_by_category,
        name='category_cocktails'
    ),
    path(
        'toggle_like_cocktail/<int:cocktail_id>/',
        views.toggle_like_cocktail,
        name='toggle_like_cocktail'
    ),
    path('favorite_cocktails/', views.favorite_cocktails, name='favorite')
]
