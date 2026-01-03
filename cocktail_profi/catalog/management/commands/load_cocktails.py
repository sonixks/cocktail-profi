import requests
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.management.base import BaseCommand
from catalog.models import Cocktail, Category, Ingredient, CocktailIngredient, MeasurementUnit
from deep_translator import GoogleTranslator


class Command(BaseCommand):
    help = 'Загрузка с использованием словарей БД'

    def handle(self, *args, **kwargs):
        self.translator = GoogleTranslator(source='auto', target='ru')
        self.units_dict = {
            u.name_en: u.name_ru
            for u in MeasurementUnit.objects.all()
        }

        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)

        letters = list('abcdefghijklmnopqrstuvwxyz')
        base_url = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={}'

        for letter in letters:
            self.stdout.write(f'>>> Буква "{letter}"...')
            try:
                response = session.get(base_url.format(letter), timeout=30)
                try:
                    data = response.json()
                except ValueError:
                    continue

                drinks = data.get('drinks')
                if drinks:
                    total = len(drinks)
                    for i, item in enumerate(drinks, 1):
                        print(f'   [{i}/{total}] {item["strDrink"][:30]}...', end='\r')
                        self.process_cocktail(item)
                    print('') 
            except Exception as e:
                print(f'Ошибка: {e}')
            time.sleep(1)

    def process_cocktail(self, item):
        try:
            ext_id = item['idDrink']
            if Cocktail.objects.filter(external_id=ext_id).exists():
                return 

            # 1. Категория
            cat_name_en = item.get('strCategory', 'Other').strip()
            category_obj = Category.objects.filter(name=cat_name_en).first()
            if not category_obj:
                try:
                    cat_name_ru = self.translator.translate(cat_name_en)
                except Exception:
                    cat_name_ru = cat_name_en
                category_obj = Category.objects.create(name=cat_name_en, name_ru=cat_name_ru)

            # 2. Коктейль
            name_en = item['strDrink']
            instr_en = item.get('strInstructions', '') or ""

            try:
                name_ru = self.translator.translate(name_en)
                instr_ru = self.translator.translate(instr_en) if instr_en else ""
            except Exception:
                name_ru = name_en
                instr_ru = instr_en

            is_alc_bool = True if item.get('strAlcoholic') == 'Alcoholic' else False

            cocktail = Cocktail.objects.create(
                external_id=ext_id,
                category=category_obj,
                name=name_en,
                name_ru=name_ru,
                instruction=instr_en,
                instruction_ru=instr_ru,
                is_alcoholic=is_alc_bool,
                image_url=item.get('strDrinkThumb', ''),
            )

            for i in range(1, 16):
                ing_key = f'strIngredient{i}'
                measure_key = f'strMeasure{i}'

                raw_ing = item.get(ing_key)
                if not raw_ing:
                    break
                clean_ing_name = raw_ing.strip()

                raw_measure = item.get(measure_key)
                clean_measure = raw_measure.strip() if raw_measure else ""
                final_amount = self.translate_measure_using_db(clean_measure)
                ingredient_obj = Ingredient.objects.filter(name__iexact=clean_ing_name).first()

                if not ingredient_obj:
                    try:
                        ing_name_ru = self.translator.translate(clean_ing_name)
                    except Exception:
                        ing_name_ru = clean_ing_name

                    ingredient_obj = Ingredient.objects.create(
                        name=clean_ing_name,
                        name_ru=ing_name_ru
                    )
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient_obj,
                    amount=final_amount
                )

        except Exception as e:
            print(f'   Err: {e}')

    def translate_measure_using_db(self, amount_str):
        if not amount_str:
            return ""

        text = amount_str.lower()
        sorted_keys = sorted(self.units_dict.keys(), key=len, reverse=True)

        for en_unit in sorted_keys:
            pattern = r'\b' + re.escape(en_unit) + r'\b'

            if re.search(pattern, text):
                ru_unit = self.units_dict[en_unit]
                text = re.sub(pattern, ru_unit, text)

        return text
