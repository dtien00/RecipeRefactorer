import clingo
    
program = """
p(@id(10)).
q(@seq(1,2)).
"""

allergen = """
% Constraints
allergic.
#program allergic(x).
:-allergen(x).
"""

ingredient = """
incorporate.
#program incorporate(x, m, q).
ingredient(x, m, q).
allergen(x):-ingredient(x, m, q).
"""

diabetes = """
:-dv_sugar(6).
:-#sum(X : ingredient(N, M, Q, ....... X)), X=>6.
"""

lactose_intolerant = """
:-allergen(\"milk\").
"""

nutritional_metrics = """
calories
,protein,TotalFat,Carbohydrate,Sodium,SaturatedFat,Cholesterol,Sugar,Calcium,Iron,Potassium,VitaminC,VitaminE,VitaminD
"""

class clingoResolver:
    def __init__(self):
        # self.ctx = ctx
        self.ctl = clingo.Control(["--enum-mode=brave"])
        self.ctl.add("incorporate", [], ingredient)
        self.ctl.add("allergic", [], allergen)


    def add_ingredient(self, ingredient: tuple[str, str, int]):
        # Add the ingredient to the ASP program
        self.ctl.ground([("incorporate", [clingo.String(ingredient[0]), clingo.String(ingredient[1]), clingo.Number(ingredient[2])])])
    
    def add_allergen(self, allergen: str):
        # Add the allergen to the ASP program
        self.ctl.ground([("allergic", [clingo.String(allergen)])])

    def on_model(m):
            print("Solution found: ", m)
            return m, True

    def resolve(self):
        # if isinstance(x, clingo.Number):
        #     return x
        # elif isinstance(x, clingo.String):
        #     return x.string
        # elif isinstance(x, clingo.Function):
        #     if x.name == "id":
        #         return self.ctx.id(*[self.resolve(arg) for arg in x.arguments])
        #     elif x.name == "seq":
        #         return self.ctx.seq(*[self.resolve(arg) for arg in x.arguments])
        # else:
        #     raise ValueError(f"Unknown type: {type(x)}")

        # INGREDIENTS FIRST, THEN CONSTRAINTS

        result = self.ctl.solve(on_model=self.on_model, yield_=True)

        if result.get().unsatisfiable:
            core = result.core()
            print("No solution found: Conflict core: ", core)
            return core, False
        else:
            return result, True