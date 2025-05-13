from models.classes import Recipe
def test_allergens(recipe : Recipe, allergens : list[str]):
        """ Test for allergens in the recipe. Returns 1 if no allergens are detected, 0 if allergens are detected.
            @args:
                recipe : Recipe object to be tested
                allergens : list of allergens to be tested against the recipe
            @return:
                1 if no allergens are detected, 0 if allergens are detected.
        """
        # print("Test A")
        ingredients = [x[0] for x in recipe.list]
        for allergen in allergens:
                for ingredient in ingredients:
                        if allergen.lower() in ingredient.lower(): return 0 # Upon detection of allergen in the recipe, return fail (0)
        return 1

def test_diabetes(recipe : Recipe, type : int):
        """ Test for diabetes in the recipe. Returns 1 if no diabetes is detected, 0 if diabetes is detected.
            @args:
                recipe : Recipe object to be tested
                type : int representing the type of diabetes (1 or 2)
            @return:
                1 if no high sugar levels are detected, else 0 if diabetes is detected.
        """
        # print("Test B")
        print(str(recipe))
        print(type)
        return 0

def test_hypertension(recipes):
        # print("Test C")
        return 0

def test_obesity(recipes):
        # print("Test D")
        return 0

def test_lactase(recipes):
        # print("Test E")
        return 0
