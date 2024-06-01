import itertools
import re

# def truth_table(formula):
#     # Replace logical operators with Python's equivalents
#     formula = formula.replace("AND", "and").replace("OR", "or").replace("NOT", "not")

#     # Find all unique capital single-letter variables (e.g., A, B, C)
#     variables = sorted(set(filter(str.isupper, formula)))

#     # Generate all possible combinations of truth values for the variables
#     truth_combinations = list(itertools.product([True, False], repeat=len(variables)))

#     # Prepare the result dictionary
#     results = []

#     # Evaluate the formula for each combination
#     for combination in truth_combinations:
#         # Create a local dictionary to evaluate the formula
#         local_env = {var: val for var, val in zip(variables, combination)}

#         # Evaluate the formula using eval in the context of local_env
#         try:
#             result = eval(formula, {}, local_env)
#         except Exception as e:
#             result = str(e)  # In case of an error in the formula

#         # Store the result along with variable values
#         results.append({**local_env, "Result": result})

#     return results


def eval_formula(formula: str, assignment):
    """Evaluates the formula given the truth assignment."""
    local_dict = assignment.copy()
    formula = formula.replace("AND", "and").replace("OR", "or").replace("NOT", "not")
    return eval(formula, {"__builtins__": None}, local_dict)


def truth_table(formula: str):
    # Find unique variables
    variables = sorted(set(re.findall(r"[A-Z]", formula)))
    # Create all combinations of truth values for these variables
    combinations = itertools.product([True, False], repeat=len(variables))
    results = {}
    for combination in combinations:
        assignment = dict(zip(variables, combination))
        # Evaluate the formula with the current assignment
        result = eval_formula(formula, assignment)
        results[tuple(sorted(assignment.items()) + [("Formula", result)])] = result
    return results
