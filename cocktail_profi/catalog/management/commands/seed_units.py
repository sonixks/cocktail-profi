from django.core.management.base import BaseCommand
from catalog.models import MeasurementUnit


class Command(BaseCommand):
    help = 'Наполняет базу единицами измерения'

    def handle(self, *args, **kwargs):
        units = {
            'oz': 'унц.',
            'ounce': 'унц.',
            'cl': 'cl',
            'ml': 'мл',
            'tsp': 'ч.л.',
            'tbsp': 'ст.л.',
            'shot': 'шот',
            'jigger': 'джиггер',
            'cup': 'чашка',
            'pint': 'пинта',
            'dash': 'дэш',
            'dashes': 'дэш',
            'splash': 'сплэш',
            'part': 'часть',
            'parts': 'частей',
            'slice': 'слайс',
            'wedge': 'долька',
            'pinch': 'щепотка',
            'piece': 'кусочек',
            'garnish': 'на украшение',
            'bottle': 'бутылка',
            'can': 'банка',
            'lb': 'фунт',
        }

        for en, ru in units.items():
            obj, created = MeasurementUnit.objects.get_or_create(
                name_en=en,
                defaults={'name_ru': ru}
            )
            if created:
                self.stdout.write(f'Добавлено: {en} -> {ru}')
            else:
                if obj.name_ru != ru:
                    obj.name_ru = ru
                    obj.save()
                    self.stdout.write(f'Обновлено: {en} -> {ru}')

        self.stdout.write(self.style.SUCCESS('Справочник измерений обновлен!'))
