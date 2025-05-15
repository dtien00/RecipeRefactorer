# Setup
Additional testing will need to be done for set up. Currently, set up dependencies using

`pip install -r requirements.txt`

Kaggle API credentials will be required, which you can generate your own at: `https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md`

After downloading the datasets, move the two resulting datafiles `full_dataset.csv` and `USDA.csv` to a folder called 'data' within the root directory of this project.

Run the program with

`python main.py`

Input:
- Dish name to pull recipe for from Recipe1M+ expanded dataset
- List of constraints: Health conditions (Hypertension/Allergens/Diabetes/Obesity)

Output:
- The recipe/ingredient list
- Corresponding nutritional manifest of the modified recipe/ingredient list

