# RecipeRefactorer
Recipe Ingredient substitutions using LLMs, databases and logic programming (LP) to create suitable safe alternatives against Obesity/Nutrition/Dietary Restrictions/Health Conditions

Input:
- URL/URI to refer to a particular recipe, or some general name for a dish
- List of constraints: Health conditions (Hypertension/Allergens/Diabetes), Unavailable/Disliked ingredients, a numerical factor to scale recipe amount made, and optional medical information (age, weight, height)

We note that many websites will include additional clutter (ads, website elements) that do not pertain to the recipe itself, so parsing will be required. The recipe itself will be presented as a table consisting of ingredients and quantity. While recipe directions were initially considered, it was deemed too subjected/multi-faceted, and we plan to only focus on the raw materials used in this recipe.

Output:
- The modified recipe/ingredient list
- Manifest of ingredients from original recipe that violated constraints gave as input
- Corresponding nutritional manifest of the modified recipe/ingredient list

The modified recipe/ingredient list will also be a table consisting of ingredients and quantity. Refer to figure 1, created in LucidChart, for a rough example of how they would be represented in the program. 

 Tools and Performance
- Percentage of aggregate substitute list in nutritional value to the original
- Calculation of proposed recipe substitution vector distance from original
- Potential feedback by user, including additional constraints or outright rejection
- Minimization on certain nutritional fields
- Comparisons of original ingredients and proposed substitutions

Examples of Solutions in important/interesting applications
- User data to determine popular/most used substitute B for ingredient A
- Feedback to determine most rejected substitutions (unpopular substitutes)
- Generalized substitutions for ingredients for individuals of certain conditions
- Possible links between condition and desired ingredient/dish to consume
- Correlation between condition and serving size scale factor (social v private)
- Correlation between nutritional benefit and financial cost of substitutions
- Correlation between age, weight, conditions, and preferences

Current ‘best’ existing methods and implementations
Identifying Ingredient substitutions Using Knowledge Graph of Food ^1
Optimizing Ingredient Substitution Using LLMs to Enhance Phytochemical Content in Recipes ^2
FoodKG; Recipe and ingredient data source, widely recognized ^3
USDA; Nutritional Information, government entity, national standard
Foodon; Food and food production ontology
FlavorDB; Flavor profile DB

Highlighted in Shirai’s paper, common techniques include classification of food types to reject based on constraints, filtering ingredients that are subclasses of prohibited types, and heuristics to determine adequate substitutions known as DIISH

Tasks/Subtasks
Classification of foodstuffs in recipe
Recognition from Foodon, predicates with food type, metric, quantity
	Removal of violating foodstuffs from constraints
Setting default false pattern matchings; default false predicates
	Substitutions
Quantity of substitution filled by weight against constraints
	Presentation
Aggregates of the ingredients and health information/nutrition
Compare reduction of nutritional fields from original to substituted
Plan
Currently not implemented, based on wording of assignment to include the problem and design







Design
API Scheme
Pure sense of the ‘what’:
Taking input from user
- Recipe/Ingredient List 
- Health Condition 
- Recipe Scaling Factor (Optional) 
- Medical Information (Optional)
Returning an ingredient list matching constraints
			- Predicate returned as result of query made to match substitutions.
			- List of ingredients and quantity of each.
		Scaling of recipe
			- Apply scaling factor to recipe default serving size, based on user input.
			- If no scaling factor provided, do nothing, treat the factor as 1.
		Presentation/Comparison
			- Metrics of reduced nutrition fields, differences.
			- Manifest of original recipe foodstuffs violating constraints.
		Acception/Rejection of substitution
			- Additional optional constraints added; foodstuffs, nutrition constraints.
			- If provided, we take this as rejection of first proposed substitutions and loop back to returning an ingredient list matching constraints as a second call.
			- If not provided, user indicates acceptance of the substituted recipe.
Components, libraries, tools, functionalities
- Intending to have the driver program implemented in Python to take user input, indicating if providing URL/URI of recipe, or a generic string for a dish by name.
- API calls to FoodKG to either get the recipe should the user provide just the general name for it, then ingredients for the obtained recipe. As part of FoodKG’s capabilities, Foodon, USDA, and potentially FlavorDB are queried to obtained the ontologies, nutritional information, and flavor profiles.
- File writing to optionally save the proposed substituted recipe for the user, preventing repeated queries for the same dish.
Moin DocTools (Python)
Will need to review the wiki later.
Complete Design Doc
Please refer to the attached pdf file for a brief description of the intended project structure and flow.

*Edited excerpt from ‘Customer wanting an automated reasoning system’
The system would first take in the desired recipe to be modified, either through a website URL/URI*4 or a general name for the dish. Then, the user is prompted to input their current health conditions and, assuming ethics allow it, the medical information pertaining to them from a health screening listing their current status, risks and recommendations such as allergens. 

Once the driver program receives the user’s input, it will make a call depending on whether a URL/URI was provided. Should it be provided, the recipe associated with the link is extracted to yield the list of ingredients for it, else should it not be a hyperlink, a query will be made to FoodKG and obtain the associated ingredients with the recipe on the Recipe1M+ database. With the list of ingredients obtained from either action taken, we make another call to FoodKG to query on our behalf the USDA database for the nutritional information for each ingredient. Afterwards, FoodKG is queried a third time to make a query to Foodon and obtain the ontologies for each of the ingredients as well. 

The order of querying the food ontologies and nutritional information is not considered to have any effect now, but still tentative should benefits be found during implementation. 

Finally, the driver program refactors the recipe, nutritional, ontology, and constraint information into grounds and predicates equivalents that can be utilized by a logic program that will determine if matching configurations of ingredients exist that satisfy the constraints. The system then returns the modified recipe with different ingredients, as well as nutritional information reflecting said changes to demonstrate the effects of the modification to reach a similar result.*3 
This system would not take into account the possibility for the user to edit the recipe to their own tastes (e.g. - 'sweeter', 'saltier'), as such terms may prove to be difficult to quantify how much for recipe modification. On the other hand, if more of the end food product is desired, the user will be able to ask for some scale (e.g. - 'double', 'half’, ‘2’, ‘½’, ‘0.5’) and the system will return proportional values, to prevent the user having to manually calculate on their own, and does not introduce the possibility of overconsumption, as even without it it is still up to the user to control the amount to eat, and they increase it regardless of their own volition. 

Another feature the system could have is for the option to declare one of the alternatives to not be available, which would prompt another recommendation that would essentially run the process again, now with an additional constraint.
It is currently still in consideration that when creating the grounds and predicates for the logic program to utilize, should the ontology data be used to declare suitable substitutes to be refactored before calling the logic program, or should the logic program itself be linked to a data file that contains predicates and grounds corresponding to relations between the foodstuffs already obtained from FoodKG’s queries to Foodon. 

The first option would require more work to be done in the driver program, and would reduce the work that would need to be done by the logic program. The second option will require less work on the driver program in contrast, but to reference a data file that contains predicates pertaining to all possible foodstuffs would be potentially more storage intensive, as it would also contain redundant ingredients that would not ever be considered as substitutes.

References
*1 Shirai, S. S., Seneviratne, O., Gordon, M. E., Chen, C., & McGuinness, D. L. (2021). Identifying ingredient substitutions using a knowledge graph of food. Frontiers in Artificial Intelligence, 3. https://doi.org/10.3389/frai.2020.621766

*2 Rita, L., Southern, J., Laponogov, I., Higgins, K., & Veselkov, K. (2024). Optimizing ingredient substitution using large language models to enhance phytochemical content in recipes. Machine Learning and Knowledge Extraction, 6(4), 2738–2752. https://doi.org/10.3390/make6040131

*3 FoodKG. (n.d.). https://foodkg.github.io/

[4] Beiser A. Beef tagine (Moroccan beef stew). GypsyPlate. Published April 17, 2024. https://gypsyplate.com/beef-tagine/


[5] fatsecret. Calories in beef tendon and nutrition facts. Fatsecret. https://www.fatsecret.com/calories-nutrition/generic/beef-tendon?frc=True

