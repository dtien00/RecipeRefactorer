#import pyautogui
import re   # For regex operations
import ast # To convert string of a list from the Kaggle dataset to a list
import easygui # For easy GUI input and output
import json # For structured data
import pandas as pd # For data manipulation and analysis
import os # For file path management
from typing import Union # For type hinting
import rapidfuzz # Utilized for fuzzy string matching recipes and ingredients
import opendatasets as od   # Used to download datasets from Kaggle
from models.classes import Query, Recipe, Dish
from error_classes.errors import TerminationError
from fractions import Fraction # Used to handle string representation of fractions into numerical values
from utilities import test_constraints as tc # Importing the test_constraints module for constraint testing
from utilities.asp import clingoResolver as cR # Importing the asp module for Answer Set Programming (ASP) logic

constraints_filepath = ".\config\constraints.json"

def print_recipe(recipe: Recipe, constraints, fail_flag: bool = False) -> None:
    """
    Writes the given recipe content to a text file in the '../output/' directory.

    :param recipe_content: The recipe content to write to the file.
    :param filename: The name of the output file (default is 'recipe_output.txt').
    """
    # Determine the output directory relative to this file's location
    output_dir = os.path.join(os.path.dirname(__file__), './output/')
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the full path to the output file
    # Use the recipe dish name and constraints to create a unique filename
    constraint_str = ""
    for constraint in constraints:
        # print(constraint, constraints[constraint], len(constraints[constraint]))
        if len(constraints[constraint]) == 0:
            constraint_str += f"{constraint}#"
        elif type(constraints[constraint]) == str:
            constraint_str += f"{constraint}_"+constraints[constraint]+"#"
        else:
            constraint_str += f"{constraint}"+"_".join(constraints[constraint])+"#"
    failed_recipe = "_failed" if fail_flag else ""
    filename=f"{recipe.dish}-{constraint_str}{failed_recipe}.txt"
    output_file_path = os.path.join(output_dir, filename)
    
    # Write the recipe content to the file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(recipe))
    
    print(f"Recipe written to {output_file_path}")

def parse_quantity(s: str) -> Union[float,None]:
    """
        Parse a string representing a quantity and convert it to a float.
        Handles mixed numbers, simple fractions, and decimals.
        @args:
            s: str - The string to parse.
        @return:
            float - The parsed quantity as a float.
            None - If the string cannot be parsed.
    """
    s = s.strip().replace(',', '')  # Remove commas (e.g., "1,000" -> "1000")
    try:
        # Mixed number: e.g., "1 1/2"
        if ' ' in s and '/' in s:
            whole, frac = s.split()
            return float(whole) + float(Fraction(frac))
        # Simple fraction: e.g., "3/4"
        elif '/' in s:
            return float(Fraction(s))
        # Decimal or integer: e.g., "1000", "0.75"
        else:
            return float(s)
    except ValueError:
        return None  # Graceful fallback

### MAIN FUNCTION ###
if __name__ == '__main__':

    # Download data set with kaggle.json credentials if not already downloaded
    # Requires kaggle.json credentials at https://drive.google.com/file/d/1kaUbHod3qou37Tw-ZKfrr7KibunJ4lNm/view?usp=sharing
    # kaggle_dir = os.path.expanduser('~/.kaggle')
    # os.makedirs(kaggle_dir, exist_ok=True)

    # kaggle_cred_path = os.path.join("credentials", "kaggle_user.json")
    # with open(kaggle_cred_path, 'r') as f:
    #     kaggle_cred = json.load(f)

    if not os.path.isfile(r"data\full_dataset.csv"):
        od.download("https://www.kaggle.com/datasets/uciml/recipe-ingredients-dataset")
    if not os.path.isfile(r"data\USDA.csv"):
        od.download("https://www.kaggle.com/datasets/demomaster/usda-national-nutrient-database")

    try:
        # Handle recipe input #
        recipe = easygui.enterbox("Enter your recipe: ", "Recipe Refactoring")
        # print(f"Recipe: {recipe}")
        if not len(recipe) or recipe==None: raise TerminationError

        # Transform .csv file into a pandas DF for ease of tabulation
        recipe_data = pd.read_csv(r"data\full_dataset.csv")
        recipe_names = recipe_data['title'].tolist()
        
        nutrition_data = pd.read_csv(r"data\USDA.csv")
        
        ### Query Recipe Database for a possible matching recipe ###
        """
            result = queryFoodDataset(recipe)
            if result == None: notifyUser("Sorry, we do not have any information on how this dish is made :(")
            else: result = parseRecipe(result)
        """
        exact_match_query = recipe_data[recipe_data['title']==recipe]
        if exact_match_query.empty: # 'not' 
            #print("Exact match found: ", exact_match_query)
        #     pass
        # else:
            # print("No exact match found.")
            ### If no exact match, offer possibly matching dishes lexigraphically ###
            recipe_matches = rapidfuzz.process.extract(recipe, recipe_names, scorer=rapidfuzz.fuzz.partial_ratio, limit=100)
            ## Randomly sample a collection of matching dishes 
            top_matches = recipe_data.iloc[[m[2] for m in recipe_matches if m[1] > 80]]
            top_matches_names = [t[0] for t in recipe_matches]
            
            dish = easygui.choicebox("Please select one of the possible matches:", "Recipe Refactoring", top_matches_names)
            exact_match_query = recipe_data[recipe_data['title']==dish]
            if exact_match_query.empty: raise TerminationError
        else:
            dish = recipe
            # print("Exact match found: ", exact_match_query)

        ### Initialize OriginalRecipe Object to store all ingredients from the recipe ###
        """
            with result as r:
                for each ingredient, quantity in r: OriginalRecipe.add(ingredient, quantity)
        """
        recipes = exact_match_query['ingredients'] # Ingredients can be of multiple variations; collection of ingredients for one recipe. Check if there is only one recipe, or multiples

        # print("Ingredients: ", recipes.to_list())
        
        ingredient_lists = exact_match_query['NER'] # Just the lists of the actual ingredients; no metrics provided for measurement
        # print("NER: ", ingredient_lists.to_list())
        
        combined = recipes.combine(ingredient_lists, lambda x, y: [x, y])
        
        if len(recipes)==1: print("Only one recipe for this dish! Wow!")
        recipe_book : list[Recipe] = [] # Store all variations of recipes and nutritional information

        # Used to parse the quantity and unit of measurement from the ingredient string
        pattern = r'^\s*(?P<quantity>(?:\d+\s\d+/\d+|\d+/\d+|\d+(?:\.\d+)?))\s*(?P<unit>oz\.?|lb\.?|g|kg|ml|l|cups?|c\.?|tbsp\.?|tablespoons?|tsp\.?|teaspoons?|pkg\.?|package|can|box|bag|envelope|jar|container|stick|bottle|slice|block)?\s+(?P<ingredient>.+)$'

        combined = combined.reset_index()
        for index, row in combined.iterrows():
            # print(recipe, type(recipe))
            # print("INDEX: ", index)
            # print("ROW: ", row)
            quantities = ast.literal_eval(row[0][0])
            ingredients = ast.literal_eval(row[0][1])

            # print("QUANTITIES: ", quantities, type(quantities))
            # print("INGREDIENT: ", ingredients, type(ingredients))
            recipe_sheet = Recipe(dish=dish)
            for index, quantity in enumerate(quantities):
                quantity_ = re.findall(pattern, quantity, re.IGNORECASE)
                # print(quantity_)
                # print("INDEX: ", index)
                if not len(quantity_): 
                    # print("NO MATCHES FOUND")
                    # recipe_sheet.add(ingredients[index], None, None)
                    recipe_sheet.add(quantity, None, None)
                else:
                    quantity_ = quantity_[0]
                    # print(f"'{quantity}' -> {quantity_}")
                    value = parse_quantity(quantity_[0])
                    metric = quantity_[1]
                    ingredient = quantity_[2]
                    # ingredient = ingredients[index]
                    print(ingredient, value, metric)
                    recipe_sheet.add(ingredient, value, metric)
            # print(f"--------")
            recipe_book.append(recipe_sheet)
            # print(recipe_book)

        # print("RECIPES...")
        # for recipe in recipe_book:
        #     print(str(recipe))
        #     print("------------")
            
        ### Compile the nutritional data for each dish based on the provided usda food nutritional data ###
        for recipe in recipe_book:
            print("-------------")
            nutrition = cR() ### Create a clingo.Control() object to help scale nutritional values based on quantity and metric to 100 gram standard
            for ingredient_info in recipe.list:
                ### Preprocessing of string representation of the ingredient to make it more compatible with USDA dataset
                ingredient_name = ingredient_info[0].lower().replace(" ", ",")
                ingredient_descriptions = ingredient_name.split(",")

                ### Find close matches with ingredient, the choose the one with the highest matching factor with rapidfuzz ###
                ingredient_names = nutrition_data['Description'].str.lower().str.strip().tolist()

                ### "egg" vs "egg,scrambled, cooked" vs "egg, boiled" ###
                ingredients_ = []
                if len(ingredient_descriptions) == 1: # If the ingredient is a single word
                    # print(ingredient_name)
                    best_ingredient_matches = rapidfuzz.process.extract(ingredient_name, ingredient_names, scorer=rapidfuzz.fuzz.partial_ratio, limit = 50)
                    for match in best_ingredient_matches:
                        descriptions = match[0].split(",")
                        if ingredient_name in descriptions:
                            ingredients_.append(match)
                    best_ingredient_matches = ingredients_
                else: # If the ingredient is a multi-word description
                    ingredient_descriptions.reverse()
                    ingredient_name=",".join(ingredient_descriptions)
                    # print(ingredient_name)
                    best_ingredient_matches = rapidfuzz.process.extract(ingredient_name, ingredient_names, scorer=rapidfuzz.fuzz.WRatio, limit = 50)
                    for match in best_ingredient_matches:
                        descriptions = match[0].split(",")
                        for desc in ingredient_descriptions:
                            if desc in descriptions:
                                ingredients_.append(match)
                if len(ingredients_): # Check if there are any matches
                    best_ingredient_matches = ingredients_

                ## best_match is a tuple: (matched string, score, index)
                # We take the first (best) match
                ### Add nutritional data to the recipe
                nutrition_entry = nutrition_data[nutrition_data['Description'].str.lower() == best_ingredient_matches[0][0].lower()]
                # print("INGREDIENT ENTRY: ", nutrition_entry)
                ingredient_descriptor = best_ingredient_matches[0][0].lower()
                if '"' in nutrition_entry['Description'].str.lower(): ingredient_descriptor.replace('"', "'")
                # print("Ingredient name: ", ingredient_descriptor) 
                # print("NUTRITION INFO: ", nutrition_entry.columns.tolist()[2:])
                ## Create clingo control object to help scale nutritional values based on quantity and metric to 100 gram standard
                nutrition_values = nutrition_entry.iloc[0, 2:].values.tolist()
                nutrition_values = [int(x * 1000) for x in nutrition_values]
                # print("NUTRITION VALUES: ", nutrition_values)

                ## Create metric for conversion predicate
                ingredient_quantity = ingredient_info[1]
                ingredient_metric = ingredient_info[2]

                # print("FOROROROR: ", ingredient_descriptor, ingredient_quantity, ingredient_metric, '\n')

                if (ingredient_metric in ["g", "g.", "grams"]): ingredient_metric = "grams"
                elif (ingredient_metric in ["c", "c.", "cups"]): ingredient_metric = "cup"
                elif (ingredient_metric in ["tbsp", "tbsp.", "tablespoons"]): ingredient_metric = "tablespoon"
                elif (ingredient_metric in ["tsp", "tsp.", "teaspoons"]): ingredient_metric = "teaspoon"
                elif (ingredient_metric in ["oz", "oz.", "ounces"]): ingredient_metric = "ounce"
                elif (ingredient_metric in ["lb", "lbs", "pounds"]): ingredient_metric = "pound"
                elif (ingredient_metric in ["kg", "kg.", "kilograms"]): ingredient_metric = "kilogram"
                elif (ingredient_metric in ["fl. oz.", "fluid ounces"]): ingredient_metric = "fluid_ounce"
                elif (ingredient_metric in ["pt", "pt.", "pints"]): ingredient_metric = "pint"
                elif (ingredient_metric in ["qt", "qt.", "quarts"]): ingredient_metric = "quart"
                elif (ingredient_metric in ["gal", "gal.", "gallons"]): ingredient_metric = "gallon"
                elif (not ingredient_metric): ingredient_metric = None

                nutrition.add_ingredient_3(ingredient_descriptor, int(ingredient_quantity), ingredient_metric)
                nutrition.add_ingredient_15(ingredient_descriptor, nutrition_values)

            # After all ingredients have been added, we can look to resolve to get aggregate data
            # print("Resolving... ", nutrition)
            nutrition.ctl.ground() # Ground the program
            results, flag = nutrition.resolve()
            # print("RESULTS & FLAG ", results, flag)
            # print(nutrition.models)

            if flag:
                sat_terms = nutrition.models
                print("SAT RESULTS: ", nutrition.models)
                print(type(nutrition.models))
                for term in sat_terms: # Incorporate into recipe nutritional values
                    if term.name == "ingredient":
                        print(term.arguments)
                    elif term.name == "total_ingredient":
                        print(term.arguments[0])
                    elif term.name == "allergen":
                        print(term.arguments[0])
                    elif term.name == "total_calories":
                        recipe.nutritional_values['Calories'] = term.arguments[0]
                    elif term.name == "total_protein":
                        recipe.nutritional_values['Protein'] = term.arguments[0]
                    elif term.name == "total_fat":
                        recipe.nutritional_values['TotalFat'] = term.arguments[0]
                    elif term.name == "total_carbs":
                        recipe.nutritional_values['Carbohydrate'] = term.arguments[0]
                    elif term.name == "total_sodium":
                        recipe.nutritional_values['Sodium']= term.arguments[0]
                    elif term.name == "total_satfat":
                        recipe.nutritional_values['SaturatedFat'] = term.arguments[0]
                    elif term.name == "total_chol":
                        recipe.nutritional_values['Cholesterol'] = term.arguments[0]
                    elif term.name == "total_sugar":
                        recipe.nutritional_values['Sugar'] = term.arguments[0]
                    elif term.name == "total_calcium":
                        recipe.nutritional_values['Calcium'] = term.arguments[0]
                    elif term.name == "total_iron":
                        recipe.nutritional_values['Iron'] = term.arguments[0]
                    elif term.name == "total_potassium":
                        recipe.nutritional_values['Potassium'] = term.arguments[0]
                    elif term.name == "total_vitamin_c":
                        recipe.nutritional_values['VitaminC'] = term.arguments[0]
                    elif term.name == "total_vitamin_e":
                        recipe.nutritional_values['VitaminE'] = term.arguments[0]
                    elif term.name == "total_vitamin_d":
                        recipe.nutritional_values['VitaminD'] = term.arguments[0]
                    elif term.name == "total_protein_pct":
                        print("Total protein %", term.arguments[0])
                    elif term.name == "total_fat_pct":
                        print("Total fat %", term.arguments[0])
                    elif term.name == "total_carb_pct":
                        print("Total carb %", term.arguments[0])
                    elif term.name == "total_satfat_pct":
                        print("Total satfat %", term.arguments[0])
                    elif term.name == "total_sugar_pct":
                        print("Total sugar %", term.arguments[0])
            else:
                print("UNSAT RESULTS: ", results, nutrition.models.symbols(terms=True))


        ### Handle constraints input ###
        with open(constraints_filepath, 'r') as file:
            constraint_data = json.load(file)
            # print(constraint_data["constraints"])
        constraint_choices = [x["name"] for x in constraint_data["constraints"]]
        constraints = easygui.multchoicebox("Enter constraints", "Recipe Refactoring", constraint_choices)
        if constraints == None:
            print("No constraints detected. Just looking for the recipe? Here it is : ", recipe_book[0])
            print_recipe(recipe_book[0], [])
            raise TerminationError

        # print(constraints)
        
        specified_constraints = {}
        for constraint in constraints:
            variant_choices = [x.get("variants", []) for x in constraint_data["constraints"] if x["name"]==constraint][0]
            variant_choices.sort()
            # print("vc ", variant_choices)
            if len(variant_choices):
                if constraint in ['Allergen']:
                    variants = easygui.multchoicebox(f"Enter {constraint} variant", "Recipe Refactoring", variant_choices)
                else:
                    variants = easygui.choicebox(f"Enter {constraint} variant", "Recipe Refactoring", variant_choices)
                if variants == None: raise TerminationError
            else:
                variants = []
            specified_constraints[constraint] = variants

        print("SPECIFIED CONSTRAINTS: ", specified_constraints)

        ### Begin Applying Constraints, checking against OriginalRecipe ###
        safe_recipes : list[Recipe] = []
        for recipe in recipe_book:
            # compatibility = cR()
            # for ingredient in recipe.list:
            #     compatibility.add_ingredient((ingredient[0], ingredient[2], ingredient[1]))

            for constraint, variants in specified_constraints.items():
                print(constraint, variants)
                flag = 0
                if constraint in ['Allergen', 'Diabetes']:
                    flag += tc.test_allergens(recipe, variants)
                else:
                    #flag = test_constraint[constraint](recipe)
                    flag += 0
                print("Constraint? ", flag)
            if flag==0: safe_recipes.append(recipe)

        if not len(safe_recipes): 
            print("Oh no, no compatible recipes were found :(! Please try again.")
            print("Printing violating recipe...")
            print_recipe(recipe_book[0], specified_constraints, fail_flag=True)
            raise TerminationError

        ### Create secondary object serving as the proposed Alternative Recipe ###
        # altRecipe = Recipe(dish = dish)

        ### Logic to find suitable substitutes for the recipe against the constraints provided ###
        """
            MUST BE EXAMINED LATER. ABANDONED FOR NOW
        """

        ### Output recipe to user ###
        print("Printing Recipe...")
        print_recipe(safe_recipes[0], specified_constraints)


    except TerminationError as t:
        print(t)

    except Exception as e:
        print(e)

    print("Exiting...")