#import pyautogui
import easygui
import json
import pandas
import os
from models.query import Query
from error_classes.errors import TerminationError

constraints_filepath = ".\config\constraints.json"

if __name__ == '__main__':
    try:
        # Handle recipe input #
        recipe = easygui.enterbox("Enter your recipe: ", "Recipe Refactoring")
        print(f"Recipe: {recipe}")
        if not len(recipe) or recipe==None: raise TerminationError

        ### If no exact match, offer possibly matching dishes lexigraphically ###
        """

        """

        ### Query Recipe Database for a possible matching recipe ###
        """
            result = queryFoodDataset(recipe)
            if result == None: notifyUser("Sorry, we do not have any information on how this dish is made :(")
            else: result = parseRecipe(result)
        """

        ### Initialize OriginalRecipe Object to store all ingredients from the recipe ###
        """
            with result as r:
                for each ingredient, quantity in r: OriginalRecipe.add(ingredient, quantity)
        """

        ### Query each ingredient from the database for nutritional information using a method call from Dish; this should probably be within the Dish object upon initialization ###
        """
            Dish.aggrNutr(OriginalRecipe.materials) : materials is collection of all (ingredient, quantity) pairs
        """

        # Handle constraints input #
        with open(constraints_filepath, 'r') as file:
            constraint_data = json.load(file)
            print(constraint_data["constraints"])
        constraint_choices = [x["name"] for x in constraint_data["constraints"]]
        constraints = easygui.multchoicebox("Enter constraints", "Recipe Refactoring", constraint_choices)
        if constraints == None: raise TerminationError

        print(constraints)
        
        specified_constraints = {}
        for constraint in constraints:
            variant_choices = [x.get("variants", []) for x in constraint_data["constraints"] if x["name"]==constraint][0]
            variant_choices.sort()
            print("vc ", variant_choices)
            if len(variant_choices):
                variant = easygui.choicebox(f"Enter {constraint} variant", "Recipe Refactoring", variant_choices)
                if variant == None: raise TerminationError
            else:
                variant = []
            specified_constraints[constraint] = variant

        print(specified_constraints)

        """
            # Clause where the user does not provide any constraints: they just want the recipe
            if not len(constraints): 
                system.out.println("No constraints were detected. Just looking for the recipe? Here it is: ", recipe_result)
                raise TerminationError
        """

        ### Load Food Ontology ###
        """
            ontologyDesc = {}
            for ingredient in OriginalRecipe.materials:
                result = parse(FoodOn.query(ingredient))
                check_existence(result)
                ontologyDesc.add(result)

            umbrellaOnt = {}
            for ont in ontologyDesc:
                result = parse(FoodOn.query_similar_food_families(ont))
                check_existence(result)
                umbrellaOnt.add(result)
        """

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

        ### Continue Applying Constraints, checking against available known foodstuffs on USDA ###
        """
            usda_data.query_against(conflicting_conditions) # Contains all available ingredient types we can use that do not violate some constraints provided, such as allergens. The other set of constraints including health conditions will be based on nutritional metrics.
        """

        ### Create secondary object serving as the proposed Alternative Recipe ###
        """
            altRecipe = new Recipe()
            altDish = new Dish()
        """

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


    except TerminationError as t:
        print(t)

    except Exception as e:
        print(e)
            
        # Construct query based on recipe and constraint input to the programming language #
        query = Query(recipe, specified_constraints)