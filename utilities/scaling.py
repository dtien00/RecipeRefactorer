import re

# def replace_float(match):
#     float_str = match.group()
#     float_val = float(float_str)
#     new_val = int(float_val * 1000)
#     return str(new_val)

# with open('E:\Academia\Grad School\Spring\'25\CSE505\Project\RecipeRefactorer2\RecipeRefactorer\data\densities_2.txt', 'r') as file:
#     data = file.read()

# pattern = r'\d+\.\d+'
# new_data = re.sub(pattern, replace_float, data)
# new_data = new_data.lower()

# with open('Untitled-3-modified.txt', 'w') as file:
#     file.write(new_data)

def sanitize_line(line):
    # Match density("...", number).
    match = re.match(r'density\("(.*)",\s*(\d+(\.\d+)?)\)\.', line)
    if match:
        string_part = match.group(1)
        number_part = match.group(2)

        if '"' in string_part:
            # Log and sanitize inner quotes
            print(f"Found problematic line: {line.strip()}")
            string_part = string_part.replace('"', "'")  # or remove them

        # Reconstruct line
        return f'density("{string_part}", {number_part}).\n'
    else:
        print(f"Invalid format: {line.strip()}")
        return None

with open("E:\Academia\Grad School\Spring'25\CSE505\Project\RecipeRefactorer2\RecipeRefactorer\data\densities_asp.lp", "r") as infile, open("cleaned.lp", "w") as outfile:
    for line in infile:
        if line.strip().startswith("density("):
            clean = sanitize_line(line)
            if clean:
                outfile.write(clean)
        else:
            outfile.write(line)  # keep other content unchanged
