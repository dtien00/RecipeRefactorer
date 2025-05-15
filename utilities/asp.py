import clingo
import os

base = """

#const daily_calories = 2000.

% As the ingredient is added, this introduces a potential allergen
allergen(N):-ingredient(N, _, _, _, _, _, _, _, _, _, _, _, _, _, _).

% Sum up total nutritional values of selected ingredients
total_calories(S) :- S = #sum { Cal, N : total_ingredient(N, Cal, _, _, _, _, _, _, _, _, _, _, _, _, _) }.
total_carbs(S)    :- S = #sum { Carbs, N : total_ingredient(N, _, _, _, Carbs, _, _, _, _, _, _, _, _, _, _) }.
total_protein(S)  :- S = #sum { P, N : total_ingredient(N, _, P, _, _, _, _, _, _, _, _, _, _, _, _) }.
total_fat(S)      :- S = #sum { F, N : total_ingredient(N, _, _, F, _, _, _, _, _, _, _, _, _, _, _) }.
total_sodium(S)   :- S = #sum { Sdm, N : total_ingredient(N, _, _, _, _, Sdm, _, _, _, _, _, _, _, _, _) }.
total_satfat(S)   :- S = #sum { SF, N : total_ingredient(N, _, _, _, _, _, SF, _, _, _, _, _, _, _, _) }.
total_chol(S)     :- S = #sum { C, N : total_ingredient(N, _, _, _, _, _, _, C, _, _, _, _, _, _, _) }.
total_sugar(S)    :- S = #sum { Sug, N : total_ingredient(N, _, _, _, _, _, _, _, Sug, _, _, _, _, _, _) }.

% Percentage of nutritional metrics in response to calories. 
%   Other metrics are minerals: no caloric value.
carb_pct(P)     :- total_calories(T), total_carbs(G), P = (G * 400) / T.
protein_pct(P)  :- total_calories(T), total_protein(G), P = (G * 400) / T.
fat_pct(P)      :- total_calories(T), total_fat(G),     P = (G * 900) / T.
satfat_pct(P)   :- total_calories(T), total_satfat(G),  P = (G * 900) / T.
sugar_pct(P)    :- total_calories(T), total_sugar(G),   P = (G * 400) / T.

% Percentage of nutritional metrics in response to daily caloric intake. 
%   Other metrics are minerals: no caloric value.
total_carb_pct(P)     :- total_carbs(G), P = (G * 400) / daily_calories.
total_protein_pct(P)  :- total_protein(G), P = (G * 400) / daily_calories.
total_fat_pct(P)      :- total_fat(G),     P = (G * 900) / daily_calories.
total_satfat_pct(P)   :- total_satfat(G),  P = (G * 900) / daily_calories.
total_sugar_pct(P)    :- total_sugar(G),   P = (G * 400) / daily_calories.

% Define conversion factors to grams
% We'll use integer scaling (values * 1000) since we can't use Python functions.
%   Essentially grams -> milligrams
conversion_factor(cup, gram, 236588).
conversion_factor(tablespoon, gram, 14787).
conversion_factor(teaspoon, gram, 4929).
conversion_factor(fluid_ounce, gram, 29574).
conversion_factor(pint, gram, 473176).
conversion_factor(quart, gram, 946353).
conversion_factor(gallon, gram, 3785410).

% Weight measurements; also grams -> milligrams
conversion_factor(gram, gram, 1000).
conversion_factor(pound, gram, 453592).
conversion_factor(ounce, gram, 28350).

% Volume to weight conversion (requires ingredient density)
convert(Ingredient, Amount, gram, Result, gram) :-
    ingredient(Ingredient, gram, Amount),
    Result = Amount.

convert(Ingredient, Amount, FromUnit, Result, ToUnit) :-
    ingredient(Ingredient, FromUnit, Amount),
    FromUnit != gram,
    conversion_factor(FromUnit, ToUnit, VolumeFactor),
    density(Ingredient, DensityFactor),
    Result = Amount * VolumeFactor * DensityFactor / (1000*1000).

% Scaling predicate of ingredient of total number of actual grams against USDA nutritional values of 100 grams.
% Due to how ordering matters in predicate definitions, having a Factor = X / 100000 
%   cannot simplify the predicate as it will be calculated by default as 0, due to no float support.
total_ingredient(N, Tc, Tp, Ttf, Tcarb, Tsod, Tsf, Tchol, Tsug, Tcal, Tiron, Tpot, Tvitc, Tvite, Tvitd):-
    convert(N, _, _, X, gram), ingredient(N, Cal, P, Tf, Carb, Sod, Sf, Chol, Sug, Calc, Iron, Pot, Vitc, Vite, Vitd),
    Tc = Cal * X / 100000, Tp = P * X / 100000, Ttf = Tf * X / 100000, Tcarb = Carb * X / 100000, Tsod = Sod * X / 100000,
    Tsf = Sf * X / 100000, Tchol = Chol * X / 100000, Tsug = Sug * X / 100000, Tcal = Calc * X / 100000,
    Tiron = Iron * X / 100000, Tpot = Pot * X/100000, Tvitc = Vitc * X / 100000, Tvite = Vite * X / 100000, Tvitd = Vitd * X / 100000.

    
#show ingredient/15.
#show total_ingredient/15.
#show total_calories/1.
#show total_carbs/1.
#show total_protein/1.
#show total_fat/1.
#show total_sodium/1.
#show total_satfat/1.
#show total_chol/1.
#show total_sugar/1.
#show carb_pct/1.
#show protein_pct/1.
#show fat_pct/1.
#show satfat_pct/1.
#show sugar_pct/1.
#show total_carb_pct/1.
#show total_protein_pct/1.
#show total_fat_pct/1.
#show total_satfat_pct/1.
#show total_sugar_pct/1.
"""

class clingoResolver:
    def __init__(self):
        # self.ctx = ctx
        self.models = []
        self.ctl = clingo.Control(["--enum-mode=brave"])
        self.ctl.add("base", [], base)

        # Add the densities from densities_asp.lp
        with open("E:\Academia\Grad School\Spring'25\CSE505\Project\RecipeRefactorer2\RecipeRefactorer\data\densities_asp.lp", "r") as file:
            for i, line in enumerate(file):
                # print(line)
                self.ctl.add(line)


    def add_ingredient_15(self, ingredient_name, nutrition_values): # ingredient is a tuple[str, int*14]
        # Add the ingredient to the ASP program
        clingo_predicate = (f"ingredient(\"{ingredient_name}\", {nutrition_values[0]}, {nutrition_values[1]},"
                            f"{nutrition_values[2]}, {nutrition_values[3]}, {nutrition_values[4]},"
                            f"{nutrition_values[5]}, {nutrition_values[6]}, {nutrition_values[7]},"
                            f"{nutrition_values[8]}, {nutrition_values[9]}, {nutrition_values[10]},"
                            f"{nutrition_values[11]}, {nutrition_values[12]}, {nutrition_values[13]})."
        )
        # print(clingo_predicate)
        self.ctl.add(clingo_predicate)
        # self.ctl.ground()
    
    def add_ingredient_3(self, ingredient_name, ingredient_quantity, ingredient_metric):
        # Add the unit to the ASP program
        if ingredient_metric == None: ingredient_metric = "gram"
        clingo_predicate = (f"ingredient(\"{ingredient_name}\", {ingredient_metric}, {ingredient_quantity}).")
        print(clingo_predicate)
        self.ctl.add(clingo_predicate)
        # self.ctl.ground()

    def add_pct_1(self, nutrition_metric, value):
        # Add the percentage to the ASP program
        clingo_predicate = (f"total_{nutrition_metric}_pct({value}).")
        self.ctl.add(clingo_predicate)

    def add_allergen(self, allergen: str):
        # Add the allergen to the ASP program
        self.ctl.add(f":-allergen(\"{allergen}\").")

    def on_model(self, m):
            print("Solution found: ", m, type(m))
            print(m.symbols(terms=True))
            print(m.symbols(shown=True))
            self.models = m.symbols(shown=True)
            return m, True

    def resolve(self):

        # INGREDIENTS FIRST, THEN CONSTRAINTS

        with self.ctl.solve(on_model=self.on_model, on_core=lambda m: print("Violations: {}".format(m)), yield_=True) as result:
            if isinstance(result, clingo.SolveHandle):
                if result.get().unsatisfiable:
                    # print("HANDLE CONFLICT ON: ", result.core())
                    return result.core(), False
                else:
                    for m in result: print("Returning SolveHandle Answer: {}".format(m))
                    return result, True
            else:
                if result.unsatisfiable:
                    # print("CONFLICT ON: ", result.core())
                    return result.core(), False
                else:
                    for m in result: print("Returning SolveResult Answer: {}".format(m))
                    return result, True