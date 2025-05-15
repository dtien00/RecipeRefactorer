class Query:
    def __init__(self, recipe_ref: str, constraints: list[str]):
        """ Represents a query for a recipe. 
            @args:
                recipe_ref : str representing the reference to the recipe
                constraints : list of constraints to be applied to the recipe
        """
        self.recipe = recipe_ref
        self.conditions = self.translate_constraints(constraints)

    @staticmethod
    def translate_constraints(constraints: list[str]):
        """ Translate the constraints into a format that can be used to query the recipe.
            <TENTATIVE> This is a placeholder function and should be replaced with actual logic.    
        """
        for constraint in constraints:
            constraint

class Recipe:
    def __init__(self, dish: str):
        """ Represents a recipe for a dish. 
            @args:
                dish : str representing the name of the dish
        """
        self.dish : str = dish
        self.list : list[tuple[str, float, str]] = []
        self.nutritional_values : dict[str, float] = {
            'Calories': 0.0,
            'Protein': 0.0,
            'TotalFat': 0.0,
            'Carbohydrate': 0.0,
            'Sodium': 0.0,
            'SaturatedFat': 0.0,
            'Cholesterol': 0.0,
            'Sugar': 0.0,
            'Calcium': 0.0,
            'Iron': 0.0,
            'Potassium': 0.0,
            'VitaminC': 0.0,
            'VitaminE': 0.0,
            'VitaminD': 0.0
        }

    def add(self, ingredient: str, quantity: float, metric: str) -> None:
        """ Add an ingredient to the recipe. 
            @args:
                ingredient : str representing the name of the ingredient
                quantity : float representing the quantity of the ingredient
                metric : str representing the metric of the ingredient (e.g. g, ml, oz, etc.)
            @return:
                None
        """
        self.list.append([ingredient, quantity, metric])
        
    
    def incorporate(self, nutrition_metric: str, nutrition_value: float) -> None:
        """ Incorporate a nutritional metric into the recipe. 
            @args:
                nutrition_metric : str representing the name of the nutritional metric
                nutrition_value : float representing the value of the nutritional metric
            @return:
                None
        """
        # for metric in nutrition_metrics:
        self.nutritional_values[nutrition_metric] += nutrition_value

    def __str__(self) -> None:
        """ String representation of the Recipe: 
                [ingredient] [quantity] [metric]
        """
        rep = f"{self.dish} Ingredients:\n-----------------------------\n"
        for item in self.list:
            rep += f"{item[0]} {item[1]} {item[2]}\n"

        rep += "\nNutritional Values:\n-----------------------------\n"
        for key, value in self.nutritional_values.items():
            rep += f"{key}: {value}\n"
        rep += "\n"
        return rep

class Dish:
    def __init__(self):
        """Represents the aggregate nutritional information for all ingredients incorporated. Similar to a nutritional label, all values are in terms of grams.
            Rewrite this as a dictionary instead; default values all 0.

            Potentially not needed. Tentative
        """