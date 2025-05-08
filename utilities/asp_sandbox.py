import clingo

allergen = """
% Constraints
#program allergic(x).
:-allergen(x).
"""

recipe = """
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
total_calories(S) :- S = #sum { Cal, N : ingredient(N, Cal, _, _, _, _, _, _, _, _, _, _, _, _, _) }.
total_carbs(S)    :- S = #sum { Carbs, N : ingredient(N, _, _, _, Carbs, _, _, _, _, _, _, _, _, _, _) }.
total_protein(S)  :- S = #sum { P, N : ingredient(N, _, P, _, _, _, _, _, _, _, _, _, _, _, _) }.
total_fat(S)      :- S = #sum { F, N : ingredient(N, _, _, F, _, _, _, _, _, _, _, _, _, _, _) }.
total_sodium(S)   :- S = #sum { Sdm, N : ingredient(N, _, _, _, _, Sdm, _, _, _, _, _, _, _, _, _) }.
total_satfat(S)   :- S = #sum { SF, N : ingredient(N, _, _, _, _, _, SF, _, _, _, _, _, _, _, _) }.
total_chol(S)     :- S = #sum { C, N : ingredient(N, _, _, _, _, _, _, C, _, _, _, _, _, _, _) }.
total_sugar(S)    :- S = #sum { Sug, N : ingredient(N, _, _, _, _, _, _, _, Sug, _, _, _, _, _, _) }.

% Percentage of nutritional metrics in response to calories
carb_pct(P)     :- total_calories(TC), total_carbs(C), P = (C * 4 * 100) / TC.
protein_pct(P)  :- total_calories(TC), total_protein(G), P = (G * 4 * 100) / TC.
fat_pct(P)      :- total_calories(TC), total_fat(G),     P = (G * 9 * 100) / TC.
satfat_pct(P)   :- total_calories(TC), total_satfat(G),  P = (G * 9 * 100) / TC.
sugar_pct(P)    :- total_calories(TC), total_sugar(G),   P = (G * 4 * 100) / TC.


% Calorie limit (example: max 2200)
:- total_calories(S), S < 1, S > 2200.

:- carb_pct(P), P > 55.
:- carb_pct(P), P < 45.

:- fat_pct(P), P > 30.
:- satfat_pct(P), P > 10.

:- protein_pct(P), P < 15.
:- protein_pct(P), P > 25.

:- sugar_pct(P), P > 10.

#show ingredient/15.

"""

diabetes = """
:-dv_sugar(6).
:-#sum(X : ingredient(N, M, Q, ....... X)), X=>6.
"""

lactose_intolerant = """
:-allergen(\"milk\").
"""

nutritional_metrics = """
calories,protein,TotalFat,Carbohydrate,Sodium,SaturatedFat,Cholesterol,Sugar,Calcium,Iron,Potassium,VitaminC,VitaminE,VitaminD
"""
# self.ctx = ctx
ctl = clingo.Control(["--enum-mode=brave"])
ctl.add("recipe", [], recipe)
ctl.add("allergic", ["x"], allergen)


ctl.ground([("recipe", [clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                        clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                        clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                        clingo.String("milk"), clingo.String("cup"), clingo.Number(2),
                        clingo.String("milk"), clingo.String("cup"), clingo.Number(2)])]) #clingo.String(ingredient[0]), clingo.String(ingredient[1]), clingo.Number(ingredient[2])

ctl.ground([("allergic", [clingo.String("milk")])])

def on_model(m):
        print("Solution found: ", m)
        return m, True

result = ctl.solve(on_model=on_model, yield_=True)

if result.get().unsatisfiable:
    core = result.core()
    print("No solution found: Conflict core: ", core)
    print("FALSE")
else:
    print("TRUE:", result.model())