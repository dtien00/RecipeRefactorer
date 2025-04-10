class Query:
    def __init__(self, recipe_ref: str, constraints: list[str]):
        self.recipe = recipe_ref
        self.conditions = self.translate_constraints(constraints)

    @staticmethod
    def translate_constraints(constraints: list[str]):
        for constraint in constraints:
            constraint