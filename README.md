# Setup
Additional testing will need to be done for set up. Currently, set up dependencies using

`pip install -r requirements.txt`

After downloading the datasets at:
- `https://www.kaggle.com/datasets/demomaster/usda-national-nutrient-database`
- `https://www.kaggle.com/datasets/saldenisov/recipenlg`

Unzip `full_dataset.csv.zip` to a folder called 'data' within the root directory of this project.
Move `USDA.csv` to the same folder called 'data' within the root directory of this project.

Run the program with

`python main.py`

Input:
- Dish name to pull recipe for from Recipe1M+ expanded dataset
- List of constraints: Health conditions (Hypertension/Allergens/Diabetes/Obesity)

Output:
- The recipe/ingredient list
- Corresponding nutritional manifest of the modified recipe/ingredient list

