import requests
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.management.base import BaseCommand
from catalog.models import Cocktail, Category, Ingredient, CocktailIngredient
from deep_translator import GoogleTranslator


class Command(BaseCommand):
    help = "Загрузка с точной конвертацией мер (oz -> мл) и переводом"

    def handle(self, *args, **kwargs):
        self.translator = GoogleTranslator(source="auto", target="ru")

        session = requests.Session()
        retry = Retry(total=3, backoff_factor=2,
                      status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Можете редактировать список букв, если часть уже загружена
        letters = list("abcdefghijklmnopqrstuvwxyz")
        url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?f={}"

        self.stdout.write(self.style.WARNING("Старт загрузки..."))

        for letter in letters:
            self.stdout.write(f'>>> Буква "{letter}"...')
            try:
                response = session.get(url.format(letter), timeout=30)
                try:
                    data = response.json()
                except ValueError:
                    continue

                drinks = data.get("drinks")
                if drinks:
                    total = len(drinks)
                    for i, item in enumerate(drinks, 1):
                        print(
                            f'   [{i}/{total}] {item["strDrink"][:30]}...', end="\r")
                        self.process_cocktail(item)
                    print("")
                else:
                    self.stdout.write("   Пусто.")

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'   Ошибка буквы "{letter}": {e}'))

            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("ГОТОВО!"))

    def process_cocktail(self, item):
        try:
            ext_id = item["idDrink"]
            if Cocktail.objects.filter(external_id=ext_id).exists():
                return

            # 1. Категория
            cat_name_en = item.get("strCategory", "Other").strip()
            category_obj = Category.objects.filter(name=cat_name_en).first()
            if not category_obj:
                try:
                    cat_name_ru = self.translator.translate(cat_name_en)
                except Exception:
                    cat_name_ru = cat_name_en
                category_obj = Category.objects.create(
                    name=cat_name_en, name_ru=cat_name_ru
                )

            # 2. Коктейль
            name_en = item["strDrink"]
            instr_en = item.get("strInstructions", "") or ""

            try:
                name_ru = self.translator.translate(name_en)
                instr_ru = self.translator.translate(
                    instr_en) if instr_en else ""
            except Exception:
                name_ru = name_en
                instr_ru = instr_en

            is_alc_bool = True if item.get(
                "strAlcoholic") == "Alcoholic" else False

            cocktail = Cocktail.objects.create(
                external_id=ext_id,
                category=category_obj,
                name=name_en,
                name_ru=name_ru,
                instruction=instr_en,
                instruction_ru=instr_ru,
                is_alcoholic=is_alc_bool,
                image_url=item.get("strDrinkThumb", ""),
            )

            # 3. Ингредиенты
            for i in range(1, 16):
                ing_key = f"strIngredient{i}"
                measure_key = f"strMeasure{i}"

                raw_ing = item.get(ing_key)
                if not raw_ing:
                    break

                clean_ing_name = raw_ing.strip()
                raw_measure = item.get(measure_key)
                clean_measure = raw_measure.strip() if raw_measure else ""

                # 3.1 Конвертация (oz -> мл)
                final_amount = self.convert_measure(clean_measure)

                # 3.2 Перевод названия
                ingredient_obj = Ingredient.objects.filter(
                    name__iexact=clean_ing_name
                ).first()
                if not ingredient_obj:
                    try:
                        ing_name_ru = self.translator.translate(clean_ing_name)
                    except Exception:
                        ing_name_ru = clean_ing_name

                    ingredient_obj = Ingredient.objects.create(
                        name=clean_ing_name, name_ru=ing_name_ru
                    )

                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient_obj,
                    amount=final_amount
                )

        except Exception as e:
            print(f"   Ошибка: {e}")

    def convert_measure(self, amount_str):
        """
        Преобразует '1 1/2 oz' -> '45 мл'.
        Простое математическое преобразование без округления до десятков.
        """
        if not amount_str:
            return ""

        text = amount_str.lower()

        # Замена дробей
        text = (
            text.replace("1/2", ".5")
            .replace("1/4", ".25")
            .replace("3/4", ".75")
            .replace("1/3", ".33")
            .replace("2/3", ".66")
        )

        # Множители
        units = {
            "oz": 30,
            "ounce": 30,
            "cl": 10,
            "ml": 1,
            "tsp": 5,
            "tbsp": 15,
            "shot": 50,
            "jigger": 45,
            "cup": 240,
            "pint": 470,
            "dash": 1,
            "splash": 5,
        }

        # Поиск числа
        match = re.search(r"(\d+(\.\d+)?)", text)

        found_unit = None
        multiplier = 0

        for unit, mult in units.items():
            if unit in text:
                found_unit = unit
                multiplier = mult
                break

        if match and found_unit:
            value = float(match.group(1))
            ml_value = value * multiplier

            # Округляем до ближайшего целого (44.3 -> 44, 44.7 -> 45)
            final_val = int(round(ml_value))

            return f"{final_val} мл"

        else:
            # Если это не цифры - переводим текст
            try:
                return self.translator.translate(amount_str)
            except Exception:
                return amount_str
