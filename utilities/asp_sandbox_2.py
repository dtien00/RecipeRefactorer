#!/usr/bin/env python3
import clingo
import sys

# Define our ASP program for cooking measurement conversions
# This version doesn't use Python scripting in ASP
asp_program = """
% Define conversion factors to grams
% We'll use integer scaling (values * 1000) since we can't use Python functions (effectively kilograms)
conversion_factor(cup, gram, 236588).
conversion_factor(tablespoon, gram, 14787).
conversion_factor(teaspoon, gram, 4929).
conversion_factor(fluid_ounce, gram, 29574).
conversion_factor(pint, gram, 473176).
conversion_factor(quart, gram, 946353).
conversion_factor(gallon, gram, 3785410).

% Weight measurements
conversion_factor(pound, gram, 453592).
conversion_factor(ounce, gram, 28350).

% Ingredient density factors (for volume to weight conversions) kg/m^3; (values * 1000)
density(flour, 530).
density(sugar, 850).
density(butter, 960).
density(milk, 1030).
density(water, 1000).
density(oil, 920).
density(rice, 780).
density(salt, 1200).
density(egg, 1030).
density(cheese, 1130).
density(cream, 1000).
density(yogurt, 1030).

% Volume to weight conversion (requires ingredient density)
convert(Amount, FromUnit, ToUnit, Result, Ingredient) :-
    ingredient(Ingredient, FromUnit, Amount),
    conversion_factor(FromUnit, ToUnit, VolumeFactor),
    density(Ingredient, DensityFactor),
    Result = Amount * VolumeFactor * DensityFactor / (1000*1000).

ingredient(flour, cup, 1). % Provides the Amount value for convert/5.

% Show the result of the conversion
#show convert/5.
"""

class CookingConversionApp:
    def __init__(self):
        self.ctl = clingo.Control()
        
        # Add the ASP program to the control object
        self.ctl.add("base", [], asp_program)
        self.ctl.ground([("base", [])])

    def convert_measurement(self, amount, from_unit, to_unit, ingredient=None):
        """Convert a measurement and return the result"""
        # Scale the amount by 1000 for precision
        scaled_amount = int(amount * 1000)
        
        # Create a program containing our query
        if ingredient:
            query = f"convert({scaled_amount}, {from_unit}, {to_unit}, Result, {ingredient})."
        else:
            query = f"convert({scaled_amount}, {from_unit}, {to_unit}, Result)."
        
        # Create a temporary program with our query
        temp_program = "query_result(Result) :- " + query
        self.ctl.add("query", [], temp_program)
        self.ctl.ground([("query", [])])
        
        # Set up a handle to collect result atoms
        handle = self.ctl.solve(yield_=True)
        
        result_value = None
        with handle as handle:
            for model in handle:
                # Extract the Result value from atoms
                for atom in model.symbols(shown=True):
                    if atom.name == "query_result":
                        # Get the result value (first argument of the atom)
                        raw_result = atom.arguments[0].number
                        # Depending on where the conversion was done, we need appropriate scaling
                        if ingredient:
                            # For ingredient conversions, we have multiple factors that need to be scaled back
                            result_value = raw_result / 1000000000
                        else:
                            # For direct conversions, scale back by dividing
                            result_value = raw_result / 1000000
        
        # Reset for next query
        self.ctl.release_external(clingo.Function("cancel"))
        self.ctl.cleanup()
        
        return result_value
    
    def run_interactive(self):
        """Run an interactive conversion shell"""
        print("Cooking Metric Conversion (type 'exit' to quit)")
        print("Example: 2.5 cups gram")
        print("Example: 1 cup gram flour")
        
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() == 'exit':
                    break
                
                # Parse user input
                parts = user_input.split()
                if len(parts) < 3:
                    print("Usage: [amount] [from_unit] [to_unit] [ingredient(optional)]")
                    continue
                
                try:
                    amount = float(parts[0])
                except ValueError:
                    print("Amount must be a number")
                    continue
                
                from_unit = parts[1]
                to_unit = parts[2]
                ingredient = parts[3] if len(parts) > 3 else None
                
                # Run the conversion
                result = self.convert_measurement(amount, from_unit, to_unit, ingredient)
                
                if result is not None:
                    if ingredient:
                        print(f"{amount} {from_unit} of {ingredient} = {result:.2f} {to_unit}")
                    else:
                        print(f"{amount} {from_unit} = {result:.2f} {to_unit}")
                else:
                    print(f"Unable to convert {from_unit} to {to_unit}")
            
            except Exception as e:
                print(f"Error: {e}")

def run_conversion_examples():
    """Run example conversions to demonstrate usage"""
    app = CookingConversionApp()
    
    examples = [
        (2.5, "cup", "gram", None),
        (1, "pound", "gram", None),
        (3, "tablespoon", "gram", None),
        (1.5, "cup", "gram", "flour"),
        (2, "cup", "gram", "sugar")
    ]
    
    print("EXAMPLE CONVERSIONS:")
    print("--------------------")
    for amount, from_unit, to_unit, ingredient in examples:
        result = app.convert_measurement(amount, from_unit, to_unit, ingredient)
        if ingredient:
            print(f"{amount} {from_unit} of {ingredient} = {result:.2f} {to_unit}")
        else:
            print(f"{amount} {from_unit} = {result:.2f} {to_unit}")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        run_conversion_examples()
    else:
        app = CookingConversionApp()
        app.run_interactive()