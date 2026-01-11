from django.db import models
from django.contrib.auth import get_user_model

from catalog.models import Ingredient

User = get_user_model()


class UserStock(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stock'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_user_stock'
    )

    class Meta:
        unique_together = ('user', 'ingredient')
