"""Day 21 challenge"""

# Built-in
import re
from time import perf_counter

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
LINE_REGEX = r"(.+) \(contains (.+)\)"


class Ingredient:
    """Ingredient used in recipes and that may contain an allergen"""

    def __init__(self, name):
        """
        Creates an ingredient with just a name
        We don't know yet if it has an allergen
        :param str name: Name of the ingredient
        """
        self.name = name
        self.allergen = None
        self.recipes = []

    def __repr__(self):
        """
        :return: String similar to how the ingredient was created
        :rtype: str
        """
        return f"Ingredient({self.name})"

    def __str__(self):
        """
        :return: String similar to how the ingredient was created
        :rtype: str
        """
        return self.__repr__()


class Allergen:
    """Allergen found in some ingredients"""

    def __init__(self, name):
        """
        Creates an allergen with just a name
        We don't know yet which ingredient causes it
        :param str name: Name of the allergen
        """
        self.name = name
        self.ingredient = None
        self.recipes = []

    def __repr__(self):
        """
        :return: String similar to how the allergen was created
        :rtype: str
        """
        return f"Allergen({self.name})"

    def __str__(self):
        """
        :return: String similar to how the allergen was created
        :rtype: str
        """
        return self.__repr__()


class Recipe:
    """Cooking recipe made of several ingredients. May contain allergens"""

    def __init__(self, line, ingredients, allergens):
        """
        Creates a recipe with a bunch of ingredients and allergens
        :param str line:
        :param [Ingredient] ingredients: Ingredient instances used in the recipe
        :param [Allergen] allergens: Allergen instances present in the recipe
        """
        self.line = line
        self.ingredients = ingredients
        self.allergens = allergens
        for instance in self.ingredients + self.allergens:
            instance.recipes.append(self)

    def __repr__(self):
        """
        :return: String similar to how the recipe was created
        :rtype: str
        """
        return f"Recipe({self.line}, {self.ingredients}, {self.allergens})"

    def __str__(self):
        """
        :return: String similar to how the recipe was created
        :rtype: str
        """
        return self.__repr__()


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_21.txt")

# Creating the objects
ingredients = {}
allergens = {}
recipes = []
for line in content:
    match = re.fullmatch(LINE_REGEX, line)
    # Maybe create ingredients
    current_ingredients = []
    ingredient_names = set(match.group(1).split(" "))
    for name in ingredient_names:
        if name not in ingredients:
            ingredient = Ingredient(name)
            ingredients[name] = ingredient
        current_ingredients.append(ingredients[name])
    # Maybe create allergens
    current_allergens = []
    allergen_names = set(match.group(2).split(", "))
    for name in allergen_names:
        if name not in allergens:
            allergen = Allergen(name)
            allergens[name] = allergen
        current_allergens.append(allergens[name])
    # Create recipe and update the ingredients/allergens
    recipe = Recipe(line, current_ingredients, current_allergens)
    recipes.append(recipe)

# --------------------------------------------------
# Problem 1: Ingredients without allergens
# --------------------------------------------------
unsolved_allergens = allergens.values()
while len(unsolved_allergens) > 0:
    unsolved_allergens = [a for a in allergens.values() if a.ingredient is None]
    for allergen in unsolved_allergens:
        # Copy the ingredient groups and remove those with known allergens
        ingredient_groups = [r.ingredients for r in allergen.recipes]
        ingredient_groups = list(
            map(lambda x: set([i for i in x if i.allergen is None]), ingredient_groups)
        )
        common_ingredients = ingredient_groups[0].intersection(*ingredient_groups[1:])
        # We cannot solve it yet
        if len(common_ingredients) > 1:
            continue
        # We have one ingredient that matches
        else:
            linked_ingredient = common_ingredients.pop()
            allergen.ingredient = linked_ingredient
            linked_ingredient.allergen = allergen

# Now we can count the number of times the non-allergen ingredients appear
ingredients_without_allergens = [i for i in ingredients.values() if i.allergen is None]
total = 0
for recipe in recipes:
    for ingredient in ingredients_without_allergens:
        if ingredient in recipe.ingredients:
            total += 1
print(total)

# --------------------------------------------------
# Problem 2: Ingredients with allergens
# --------------------------------------------------
ingredients_with_allergens = [i for i in ingredients.values() if i.allergen is not None]
ingredients_with_allergens.sort(key=lambda x: x.allergen.name)
names = [i.name for i in ingredients_with_allergens]
print(",".join(names))


# Terminate
end = perf_counter()
print(end - start)
