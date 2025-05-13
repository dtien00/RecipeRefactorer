import clingo
import os

allergen = """
% Constraints
#program allergic(x).
:-allergen(X).
"""

ingredient = """
% Ingredient facts
#program ingredient(n, cal, p, f, c, sdm, sf, chol, sug, ca, fe, k, vc, ve, vd).
"""

base = """
#const calorie_limit = 2000.
#const carbohydrate_ratio = 50.
#const sugar_ratio = 10.
#const protein_ratio = 20.
#const fat_ratio = 30.
#const saturated_fat_ratio = 10.
#const sodium_ratio = 5.
#const cholesterol_ratio = 5.

% As the ingredient is added, this introduces a potential allergen
allergen(N):-ingredient(N, _, _, _, _, _, _, _, _, _, _, _, _, _, _).

% Sum up total nutritional values of selected ingredients
total_calories(X) :- S = #sum { Cal, N : ingredient(N, Cal, _, _, _, _, _, _, _, _, _, _, _, _, _) }, X = S/100.
total_carbs(X)    :- S = #sum { Carbs, N : ingredient(N, _, _, _, Carbs, _, _, _, _, _, _, _, _, _, _) }, X = S/100.
total_protein(X)  :- S = #sum { P, N : ingredient(N, _, P, _, _, _, _, _, _, _, _, _, _, _, _) }, X = S/100.
total_fat(X)      :- S = #sum { F, N : ingredient(N, _, _, F, _, _, _, _, _, _, _, _, _, _, _) }, X = S/100.
total_sodium(X)   :- S = #sum { Sdm, N : ingredient(N, _, _, _, _, Sdm, _, _, _, _, _, _, _, _, _) }, X = S/100.
total_satfat(X)   :- S = #sum { SF, N : ingredient(N, _, _, _, _, _, SF, _, _, _, _, _, _, _, _) }, X = S/100.
total_chol(X)     :- S = #sum { C, N : ingredient(N, _, _, _, _, _, _, C, _, _, _, _, _, _, _) }, X = S/100.
total_sugar(X)    :- S = #sum { Sug, N : ingredient(N, _, _, _, _, _, _, _, Sug, _, _, _, _, _, _) }, X = S/100.

% Percentage of nutritional metrics in response to calories
carb_pct(P)     :- total_calories(TC), total_carbs(C), P = (C * 4 * 100) / TC.
protein_pct(P)  :- total_calories(TC), total_protein(G), P = (G * 4 * 100) / TC.
fat_pct(P)      :- total_calories(TC), total_fat(G),     P = (G * 9 * 100) / TC.
satfat_pct(P)   :- total_calories(TC), total_satfat(G),  P = (G * 9 * 100) / TC.
sugar_pct(P)    :- total_calories(TC), total_sugar(G),   P = (G * 4 * 100) / TC.


% Calorie limit (example: max 2200)
%:- total_calories(S), S > 2200.

%:- carb_pct(P), P > 55.
%:- carb_pct(P), P < 45.

%:- fat_pct(P), P > 30.
%:- satfat_pct(P), P > 10.

%:- protein_pct(P), P < 15.
%:- protein_pct(P), P > 25.

%:- sugar_pct(P), P > 10.

% Define conversion factors to grams
% We'll use integer scaling (values * 1000) since we can't use Python functions
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

ingredient(flour, 35700,690,34,8310,5500,9,0,352,6500,138,100100,380,25,0).

% Scaling predicate of ingredient of total number of actual grams against USDA nutritional values of 100 grams.
% Due to how ordering matters in predicate definitions, having a Factor = X / 10000 cannot simplify the predicate as it will be calculated by default as 0, due to no float support.
total_ingredient(N, Tc, Tp, Ttf, Tcarb, Tsod, Tsf, Tchol, Tsug, Tcal, Tiron, Tpot, Tvitc, Tvite, Tvitd):-
    convert(N, _, _, X, gram), ingredient(N, Cal, P, Tf, Carb, Sod, Sf, Chol, Sug, Calc, Iron, Pot, Vitc, Vite, Vitd),
    Tc = Cal * X / 10000, Tp = P * X / 10000, Ttf = Tf * X / 10000, Tcarb = Carb * X / 10000, Tsod = Sod * X / 10000,
    Tsf = Sf * X / 10000, Tchol = Chol * X / 10000, Tsug = Sug * X / 10000, Tcal = Calc * X / 10000,
    Tiron = Iron * X / 10000, Tpot = Pot * X/10000, Tvitc = Vitc * X / 10000, Tvite = Vite * X / 10000, Tvitd = Vitd * X / 10000.

% Ingredient density factors (for volume to weight conversions)
density(flour, 530).
density(sugar, 850).
density(butter, 960).
density(milk, 1030).
density(water, 1000).
density(oil, 920).
density(rice, 780).
density(salt, 1200).

% Volume to weight conversion (requires ingredient density)
convert(Amount, FromUnit, ToUnit, Result, Ingredient) :-
    ingredient(Ingredient, FromUnit, Amount),
    conversion_factor(FromUnit, ToUnit, VolumeFactor),
    density(Ingredient, DensityFactor),
    Result = Amount * VolumeFactor * DensityFactor.

    
#show ingredient/15.
#show total_ingredient/15.
#show total_calories/1.
#show allergen/1.
#show total_carbs/1.
"""

diabetes = """
:-dv_sugar(6).
:-#sum(X : ingredient(N, M, Q, ....... X)), X=>6.
"""

nutritional_metrics = """
calories,protein,TotalFat,Carbohydrate,Sodium,SaturatedFat,Cholesterol,Sugar,Calcium,Iron,Potassium,VitaminC,VitaminE,VitaminD
"""

conversion = """

"""

class clingoResolver:
    def __init__(self):
        # self.ctx = ctx
        self.models = []
        self.ctl = clingo.Control(["--enum-mode=brave"])
        self.ctl.add("base", [], base)
        with open("E:\Academia\Grad School\Spring'25\CSE505\Project\RecipeRefactorer2\RecipeRefactorer\data\densities_asp.lp", "r") as file:
            for i, line in enumerate(file):
                # print(line)
                self.ctl.add(line)
        # self.ctl.ground([("base", [])])


    def add_ingredient(self, ingredient: tuple[str, str, int]):
        # Add the ingredient to the ASP program
        self.ctl.add("ingredient(milk,6300,333,346,474,5700,76,200,0,12800,5,13900,90,0,0).") 
                                        # [(f"ingredient", [clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                                        # clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                                        # clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                                        # clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                                        # clingo.String("milk"), clingo.String("cup"), clingo.Number(2)])]
        self.ctl.ground()
    
    def add_allergen(self, allergen: str):
        # Add the allergen to the ASP program
        self.ctl.add(f":-allergen(\"{allergen}\").") # [(f"allergic_{allergen}", [], [clingo.String(f"allergen({allergen})")])]
        self.ctl.ground()

    def on_model(self, m):
            print("Solution found: ", m)
            self.models.append(m)
            return m, True

    def resolve(self):

        # INGREDIENTS FIRST, THEN CONSTRAINTS

        with self.ctl.solve(on_model=self.on_model, on_core=lambda m: print("Violations: {}".format(m)), yield_=True) as result:
            
            # return result
            print("RESULT?! ", result)
            predicates = []
            if isinstance(result, clingo.SolveHandle):
                if result.get().unsatisfiable:
                    print("HANDLE CONFLICT ON: ", result.core())
                    return result.core(), False
                else:
                    for m in result: print("Returning SolveHandle Answer: {}".format(m))
                    return result, True
            else:
                if result.unsatisfiable:
                    print("CONFLICT ON: ", result.core())
                    return result.core(), False
                else:
                    for m in result: print("Returning SolveResult Answer: {}".format(m))
                    return result, True