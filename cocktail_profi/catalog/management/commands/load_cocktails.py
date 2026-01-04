from contextlib import suppress
import requests
import string
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.management.base import BaseCommand
from catalog.models import (
    Cocktail,
    Category,
    Ingredient,
    CocktailIngredient,
    MeasurementUnit
)
from deep_translator import GoogleTranslator


class Command(BaseCommand):
    help = 'Загрузка с использованием словарей БД'

    def handle(self, *args, **kwargs):
        self.translator = GoogleTranslator(source="auto", target="ru")
        self.units_dict = dict(MeasurementUnit.objects.values_list(
            "name_en",
            "name_ru"
        ))

        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(500, 502, 503, 504)
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))

        base_url = """
        https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}
        """

        for letter in string.ascii_lowercase:
            self.stdout.write(f'>>> Буква "{letter}"...')

            try:
                response = session.get(
                    base_url.format(letter=letter),
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, ValueError) as e:
                self.stderr.write(f"Ошибка для '{letter}': {e}")
            else:
                drinks = data.get("drinks") or []
                total = len(drinks)

                for i, item in enumerate(drinks, 1):
                    name = (item.get("strDrink") or "")[:30]
                    print(f"   [{i}/{total}] {name}...", end="\r")
                    self.process_cocktail(item)

                if total:
                    print()

            time.sleep(1)

    def process_cocktail(self, item):
        ext_id = item.get("idDrink")
        if not ext_id:
            return

        if Cocktail.objects.filter(external_id=ext_id).exists():
            return

        cat_name_en = (item.get("strCategory") or "Other").strip()
        cat_name_ru = cat_name_en
        with suppress(Exception):
            cat_name_ru = self.translator.translate(cat_name_en)

        category_obj, _ = Category.objects.get_or_create(
            name=cat_name_en,
            defaults={"name_ru": cat_name_ru},
        )

        name_en = (item.get("strDrink") or "").strip()
        if not name_en:
            return

        instr_en = item.get("strInstructions") or ""

        name_ru, instr_ru = name_en, instr_en
        with suppress(Exception):
            name_ru = self.translator.translate(name_en)
            instr_ru = self.translator.translate(instr_en) if instr_en else ""

        cocktail = Cocktail.objects.create(
            external_id=ext_id,
            category=category_obj,
            name=name_en,
            name_ru=name_ru,
            instruction=instr_en,
            instruction_ru=instr_ru,
            is_alcoholic=(item.get("strAlcoholic") == "Alcoholic"),
            image_url=item.get("strDrinkThumb") or "",
        )

        for i in range(1, 16):
            raw_ing = item.get(f"strIngredient{i}")
            if not raw_ing:
                break

            ing_name_en = raw_ing.strip()

            raw_measure = item.get(f"strMeasure{i}")
            measure = raw_measure.strip() if raw_measure else ""
            amount = self.translate_measure_using_db(measure)

            ingredient_obj = Ingredient.objects.filter(
                name__iexact=ing_name_en
            ).first()
            if ingredient_obj is None:
                ing_name_ru = ing_name_en
                with suppress(Exception):
                    ing_name_ru = self.translator.translate(ing_name_en)

                ingredient_obj = Ingredient.objects.create(
                    name=ing_name_en,
                    name_ru=ing_name_ru,
                )

            CocktailIngredient.objects.create(
                cocktail=cocktail,
                ingredient=ingredient_obj,
                amount=amount,
            )

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
