from django.urls import path

from bar import views

app_name = 'bar'

urlpatterns = [
    path('', views.my_bar_view, name='index'),
    path('add/<int:ingredient_id>/', views.add_ingredient, name='add'),
    path('remove/<int:ingredient_id>/', views.remove_ingredient, name='remove')
]
