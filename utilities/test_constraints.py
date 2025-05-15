from models.classes import Recipe
from utilities.asp import clingoResolver as cR # Importing the asp module for Answer Set Programming (ASP) logic
def test_allergens(recipe : Recipe, allergens : list[str]):
        """ Test for allergens in the recipe. Returns 1 if no allergens are detected, 0 if allergens are detected.
            @args:
                recipe : Recipe object to be tested
                allergens : list of allergens to be tested against the recipe
            @return:
                0 if no allergens are detected, 1 if allergens are detected.
        """
        # print("Test A")
        ingredients = [x[0] for x in recipe.list]
        for allergen in allergens:
                for ingredient in ingredients:
                        if allergen.lower() in ingredient.lower(): return 1 # Upon detection of allergen in the recipe, return fail (0)
        return 0

def test_diabetes(recipe : Recipe, type : int):
        """ Test for diabetes in the recipe. Returns 1 if no diabetes is detected, 0 if diabetes is detected.
            @args:
                recipe : Recipe object to be tested
                type : int representing the type of diabetes (1 or 2)
            @return:
                0 if no high sugar levels are detected, else 1 if diabetes is detected.
        """
        diabetic = cR()
        for nv in recipe.nutritional_values:
                value = int(recipe.nutritional_values[nv])
                if nv == "Sugar": diabetic.add_pct_1("sugar", value)
                elif nv == "SaturatedFat": diabetic.add_pct_1("satfat", value)
                elif nv == "TotalFat": diabetic.add_pct_1("fat", value)
                elif nv == "Protein": diabetic.add_pct_1("protein", value)
                elif nv == "Carbohydrate": diabetic.add_pct_1("carb", value)
        clingo_predicate = (f""":-total_carb_pct(P), P > 50."""
                            f""":-total_protein_pct(P), P > 20."""
                            f""":-total_fat_pct(P), P > 35.""") if type == 1 else (
                                f""":-total_carb_pct(P), P > 50."""
                                f""":-total_protein_pct(P), P > 25."""
                                f""":-total_fat_pct(P), P > 35.""")
        diabetic.ctl.add(clingo_predicate)
        diabetic.ctl.ground()

        results, flag = diabetic.resolve()
        print("Results: ", results, flag)
        if not flag: return 1 # On SAT, approve this. On UNSAT, reject this
        return 0

def test_hypertension(recipe: Recipe):
        # print("Test C")
        hypertension = cR()
        for nv in recipe.nutritional_values:
                value = int(recipe.nutritional_values[nv])
                if nv == "Sugar": hypertension.add_pct_1("sugar", value)
                elif nv == "SaturatedFat": hypertension.add_pct_1("satfat", value)
                elif nv == "TotalFat": hypertension.add_pct_1("fat", value)
                elif nv == "Protein": hypertension.add_pct_1("protein", value)
                elif nv == "Carbohydrate": hypertension.add_pct_1("carb", value)
        clingo_predicate = (f""":-total_satfat_pct(P), P > 6."""
                            f""":-total_fat_pct(P), P > 27."""
                            f""":-total_protein_pct(P), P > 10."""
                            f""":-total_carb_pct(P), P > 55.""")
        hypertension.ctl.add(clingo_predicate)
        hypertension.ctl.ground()
        results, flag = hypertension.resolve()
        print("Results: ", results, flag)
        if not flag: return 1 # On SAT, approve this. On UNSAT, reject this
        return 0

def test_obesity(recipe: Recipe):
        # print("Test D")
        obesity = cR()
        for nv in recipe.nutritional_values:
                value = int(recipe.nutritional_values[nv])
                if nv == "Sugar": obesity.add_pct_1("sugar", value)
                elif nv == "SaturatedFat": obesity.add_pct_1("satfat", value)
                elif nv == "TotalFat": obesity.add_pct_1("fat", value)
                elif nv == "Protein": obesity.add_pct_1("protein", value)
                elif nv == "Carbohydrate": obesity.add_pct_1("carb", value)
        clingo_predicate = (f""":-total_fat_pct(P), P > 35."""
                            f""":-total_carb_pct(P), P > 65.""")
        obesity.ctl.add(clingo_predicate)
        obesity.ctl.ground()
        results, flag = obesity.resolve()
        print("Results: ", results, flag)
        if not flag: return 1 # On SAT, approve this. On UNSAT, reject this
        return 0
