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

def print_recipe(recipe: Recipe, constraints):
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
    filename=f"{recipe.dish}-{constraint_str}.txt"
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

if __name__ == '__main__':

    # Download data set with kaggle.json credentials if not already downloaded
    # Requires kaggle.json credentials at https://drive.google.com/file/d/1kaUbHod3qou37Tw-ZKfrr7KibunJ4lNm/view?usp=sharing
    # kaggle_dir = os.path.expanduser('~/.kaggle')
    # os.makedirs(kaggle_dir, exist_ok=True)

    kaggle_cred_path = os.path.join("credentials", "kaggle_user.json")
    with open(kaggle_cred_path, 'r') as f:
        kaggle_cred = json.load(f)

    # od.download("https://www.kaggle.com/datasets/demomaster/usda-national-nutrient-database")
    # od.download("https://www.kaggle.com/datasets/uciml/recipe-ingredients-dataset")
    # exit(0)


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
        # print("Making Recipes of: ", exact_match_query, type(exact_match_query))

        recipes = exact_match_query['ingredients'] # Ingredients can be of multiple variations; collection of ingredients for one recipe. Check if there is only one recipe, or multiples

        print("Ingredients: ", recipes.to_list())
        
        ingredient_lists = exact_match_query['NER'] # Just the lists of the actual ingredients; no metrics provided for measurement
        print("NER: ", ingredient_lists.to_list())
        
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

        # print("RECIPES: VVVV")
        # for recipe in recipe_book:
        #     print(str(recipe))
        #     print("------------")
            
        ### Compile the nutritional data for each dish based on the provided usda food nutritional data ###
        for recipe in recipe_book:
            print("-------------d")
            for ingredient_info in recipe.list:
                ### Preprocessing of string representation of the ingredient to make it more compatible with USDA dataset
                ingredient_name = ingredient_info[0].lower().replace(" ", ",")
                ingredient_descriptions = ingredient_name.split(",")
                
                ### Find close matches with ingredient, the choose the one with the highest matching factor with rapidfuzz ###
                ingredient_names = nutrition_data['Description'].str.lower().str.strip().tolist()

                ### "egg" vs "parmesan,cheese"
                ingredients_ = []
                if len(ingredient_descriptions) == 1:
                    print(ingredient_name)
                    best_ingredient_matches = rapidfuzz.process.extract(ingredient_name, ingredient_names, scorer=rapidfuzz.fuzz.partial_ratio, limit = 50)
                    for match in best_ingredient_matches:
                        descriptions = match[0].split(",")
                        if ingredient_name in descriptions:
                            ingredients_.append(match)
                    best_ingredient_matches = ingredients_
                else:
                    ingredient_descriptions.reverse()
                    ingredient_name=",".join(ingredient_descriptions)
                    print(ingredient_name)
                    best_ingredient_matches = rapidfuzz.process.extract(ingredient_name, ingredient_names, scorer=rapidfuzz.fuzz.WRatio, limit = 50)
                    for match in best_ingredient_matches:
                        descriptions = match[0].split(",")
                        for desc in ingredient_descriptions:
                            if desc in descriptions:
                                ingredients_.append(match)
                if len(ingredients_):
                    best_ingredient_matches = ingredients_

                ## best_match is a tuple: (matched string, score, index)
                # matched_description, score, index = best_match
                # matched_row = df.iloc[index]
                # print("Ingredient match : ", best_ingredient_matches, "->", best_ingredient_matches[0][0])
                ### Add nutritional data to the recipe
                nutrition_entry = nutrition_data[nutrition_data['Description'].str.lower() == best_ingredient_matches[0][0].lower()]
                # print(nutrition_entry)
                # print(nutrition_entry.columns.tolist()[2:])
                for field in nutrition_entry.columns.tolist()[2:]: # Remove the first two columns (ID, Description)
                    recipe.incorporate(field, nutrition_entry[field].values[0])

        ## Validate nutritional information ###
        # for recipe in recipe_book:
        #     print(recipe.nutritional_values)

        ### Handle constraints input ###
        with open(constraints_filepath, 'r') as file:
            constraint_data = json.load(file)
            # print(constraint_data["constraints"])
        constraint_choices = [x["name"] for x in constraint_data["constraints"]]
        constraints = easygui.multchoicebox("Enter constraints", "Recipe Refactoring", constraint_choices)
        if constraints == None: raise TerminationError

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

        """
            # Clause where the user does not provide any constraints: they just want the recipe
            if not len(constraints): 
                system.out.println("No constraints were detected. Just looking for the recipe? Here it is: ", recipe_result)
                raise TerminationError
        """
        if not len(constraints):
            print("No constraints detected. Just looking for the recipe? Here it is : ", recipe_book[0])
            raise TerminationError

        ### Begin Applying Constraints, checking against OriginalRecipe ###
        """
            conflicting_conditions = {}
            for constraint in constraints:
                type_flag = 1 if consumableType(constraint) else 0
                conflicting_ingredients = OriginalRecipe.check_against(constraint, type_flag) # type_flag = {0,1}, if it is a nutritional metric constraint, or food type constraint respectively
                if conflicting_ingredients: conflicting_conditions.add(conflicting_ingredients)

            if not len(conflicting_conditions): 
                system.out.println("Congratulations!!! No constraints have been violated in the dish. Enjoy this recommended recipe: ")
                raise TerminationError

            system.out.println("It appears that the following constraints were violated as part of the recipe: ", conflicting_conditions, " let's refactor this!")
        """
        # test_constraint = {
        #     'Allergen' : tc.test_allergens,
        #     'Celiac Disease' : tc.test_gluten,
        #     'Diabetes' : tc.test_diabetes,
        #     'Hypertension' : tc.test_hypertension,
        #     'Lactose Intolerant': tc.test_lactase,
        #     'Obesity' : tc.test_obesity,
        # }
        # safe_recipes : list[Recipe] = []
        # for recipe in recipe_book:
        #     for constraint, variants in specified_constraints.items():
        #         print(constraint, variants)
        #         if constraint in ['Allergen', 'Diabetes']:
        #             flag = test_constraint[constraint](recipe, variants)
        #         else:
        #             flag = test_constraint[constraint](recipe)
        #         print("Constraint? ", flag)
        #         if flag: safe_recipes.append(recipe)

        safe_recipes : list[Recipe] = []
        for recipe in recipe_book:
            # compatibility = cR()
            # for ingredient in recipe.list:
            #     compatibility.add_ingredient((ingredient[0], ingredient[2], ingredient[1]))

            for constraint, variants in specified_constraints.items():
                print(constraint, variants)
                flag = 0
                if constraint in ['Allergen']:
                    flag += tc.test_allergens(recipe, variants)
                else:
                    #flag = test_constraint[constraint](recipe)
                    flag += 0
                print("Constraint? ", flag)
            if flag: safe_recipes.append(recipe)

        if not len(safe_recipes): print("Oh no, no compatible recipes were found :(. Let's try and make one!")


        ### Create secondary object serving as the proposed Alternative Recipe ###
        altRecipe = Recipe(dish = dish)
        

        ### Logic to find suitable substitutes for the recipe against the constraints provided ###
        """
            MAJORITY OF COMPLEXITY OF THE CODE. MUST BE EXAMINED LATER IN THE WEEK TO DETERMINE FEASABILITY
        """

        ### Check nutritional metric constraints against all possible alternate Recipes and Dishes created ###
        """
            viableRecipes = {}
            for altRecipe in altRecipes:
                if altRecipe.checks_against(constraints): viableRecipes.add(altRecipe)
        """

        ### Output recipes to user ###
        """
            if not len(viableRecipes):
                System.out.println(f"Unfortunately, it looks like no viable alternative recipes for {recipe_name} can be produced that satisfies the constraints provided earlier. Bye bye dish :(")
                raise TerminationError
            else
                System.out.println(f"Congratulations!!! We were able to find {len(viableRecipes)} alternative recipes for {recipe_name} that satisfied the constraints you provided earlier. In no particualr order, the first one is: ")
                candidate = recipes.pop()
                System.out.println(candidate)
                acception = user.input("Are you happy with this?") # acception = {0,1}, meaning rejected or accepted respectively
                if acception:
                    recipe.printToFile(candidate, ".\saved_recipes\<dish>\parse(constraints).txt")
        """

        ### Handle manual rejection by user until acceptance: We can roll this into the section above ^^^ ###
        """
            candidate = recipes.pop()
            System.out.println("How is this recipe? ", candidate)
            acception = 0
            while not acception:
                acception = user.input("Are you happy with this?") # acception = {0,1}, meaning rejected or accepted respectively
                if acception:
                    recipe.printToFile(candidate, ".\saved_recipes\<dish>\parse(constraints).txt")
        """

        ### Allow additional constraints to be retroactively added ###
        """
            additional_constraints = user.input()
        """

        ### Continue until either recipes run out, or the user finds an acceptable on. We could also roll this into the above section too ^^^ ###
        """
            while not accepted:
                candidate = recipes.pop()
                accepted = user.input("Are you happy with this?")
                if accepted:
                    System.out.println(f"Congratulations!!! We were able to find {len(viableRecipes)} alternative recipes for {recipe_name} that satisfied the constraints you provided earlier. In no particualr order, the first one is: ")
                    candidate = recipes.pop()
                    System.out.println(candidate)
                if not len(recipes):
                    system.out.println("It appears we've sadly exhausted every possible substitution for the dish of {recipe_name}. :()")
                    raise TerminationError
        """

        ### Outputting the accepted recipe as output/answer/presentation ###
        """
            system.out.println(candidate)
            system.out.println(candidate.recipe)
            system.out.println(candidate.nutritional_information)

            system.compareRecipes(candidate, originalRecipe)
        """
        print("PRINTING RECIPE")
        print_recipe(safe_recipes[0], specified_constraints)


    except TerminationError as t:
        print(t)

    except Exception as e:
        print(e)

    ### LOGIC PROGRAMMING IMPLEMENTATION ###
            
    # Construct query based on recipe and constraint input to the programming language #
    # print("result: ", recipe, specified_constraints)
    #query = Query(recipe, specified_constraints)

    example = cR()
    example.add_ingredient(("milk", "cup", 1))
    example.add_allergen("milk")
    print("Resolving... ", example)
    results, flag = example.resolve()

    if flag:
        print("SAT RESULTS: ", results, example.models[0].symbols(terms=True))
    else:
        print("UNSAT RESULTS: ", results, example.models.symbols(terms=True))