import itertools
import re
import unittest
from typing import Dict, List, Tuple


def parse_formula(formula: str, assignment: Dict[str, bool]) -> bool:
    """Safely parse and evaluate the logical formula."""
    local_dict = assignment.copy()
    formula = formula.replace("AND", "and").replace("OR", "or").replace("NOT", "not")
    try:
        return eval(formula, {"__builtins__": None}, local_dict)
    except Exception as e:
        raise ValueError("Invalid formula.") from e


def truth_table(formula: str) -> Dict[Tuple[str, bool], bool]:
    variables = sorted(set(re.findall(r"\b[A-Z]\b", formula)))
    combinations = itertools.product([True, False], repeat=len(variables))
    results = {}
    for combination in combinations:
        assignment = dict(zip(variables, combination))
        result = parse_formula(formula, assignment)
        key = tuple((var, assignment[var]) for var in variables)
        results[key] = result
    return results


class Literal:
    def __init__(self, variable: str, positive: bool = True):
        self.variable = variable
        self.positive = positive

    def __str__(self):
        if not self.positive:
            return f"NOT {self.variable}"
        return self.variable

    def __eq__(self, other):
        return (
            isinstance(other, Literal)
            and self.variable == other.variable
            and self.positive == other.positive
        )

    def __hash__(self):
        return hash((self.variable, self.positive))


class Clause:
    def __init__(self, literals: List[Literal]):
        self.literals = literals

    def __str__(self):
        return " v ".join(str(lit) for lit in self.literals)

    def __eq__(self, other):
        return isinstance(other, Clause) and set(self.literals) == set(other.literals)

    def __hash__(self):
        return hash(tuple(sorted(self.literals, key=lambda lit: lit.variable)))


def resolution(clause1: Clause, clause2: Clause) -> Clause | None:
    literals1 = set(clause1.literals)
    literals2 = set(clause2.literals)
    complementary_literals = set()

    for lit1 in literals1:
        for lit2 in literals2:
            if lit1.variable == lit2.variable and lit1.positive != lit2.positive:
                complementary_literals.add((lit1, lit2))

    if not complementary_literals:
        return None

    result_literals = literals1 | literals2
    for lit1, lit2 in complementary_literals:
        result_literals.discard(lit1)
        result_literals.discard(lit2)

    return Clause(list(result_literals))


def inference(
    knowledge_base: List[Clause], query: Clause, max_iterations: int = 100
) -> bool:
    negated_query = Clause(
        [Literal(lit.variable, not lit.positive) for lit in query.literals]
    )

    # Check if the negated query already exists in the knowledge base
    for clause in knowledge_base:
        if negated_query == clause:
            return True

    clauses = set(knowledge_base + [negated_query])
    new_clauses = set()

    for _ in range(max_iterations):
        pairs = [(c1, c2) for c1 in clauses for c2 in clauses if c1 != c2]
        for c1, c2 in pairs:
            resolvent = resolution(c1, c2)
            if resolvent is not None:
                if not resolvent.literals:
                    return True
                new_clauses.add(resolvent)

        if not new_clauses - clauses:
            break
        clauses.update(new_clauses)
        new_clauses.clear()

    return False


class TestPropositionalLogic(unittest.TestCase):
    def test_truth_table_simple(self):
        formula = "(A or B)"
        expected_table = {
            (("A", True), ("B", True)): True,
            (("A", True), ("B", False)): True,
            (("A", False), ("B", True)): True,
            (("A", False), ("B", False)): False,
        }
        self.assertEqual(truth_table(formula), expected_table)

    def test_truth_table_negation(self):
        formula = "NOT A"
        expected_table = {
            (("A", True),): False,
            (("A", False),): True,
        }
        self.assertEqual(truth_table(formula), expected_table)

    def test_truth_table_complex(self):
        formula = "(A and B) or (C and NOT D)"
        variables = ["A", "B", "C", "D"]
        combinations = itertools.product([True, False], repeat=len(variables))
        expected_table = {}
        for combination in combinations:
            assignment = dict(zip(variables, combination))
            result = parse_formula(formula, assignment)
            key = tuple(sorted(assignment.items()))
            expected_table[key] = result

        actual_results = truth_table(formula)
        self.assertEqual(actual_results, expected_table)

    def test_resolution_contradiction(self):
        clause1 = Clause([Literal("A")])
        clause2 = Clause([Literal("A", False)])
        expected_clause = Clause([])
        self.assertEqual(str(resolution(clause1, clause2)), str(expected_clause))

    def test_resolution_no_contradiction(self):
        clause1 = Clause([Literal("A"), Literal("B")])
        clause2 = Clause([Literal("C"), Literal("D")])
        expected_clause = None  # Expecting None since no resolution should occur
        self.assertEqual(resolution(clause1, clause2), expected_clause)

    def test_inference_entailment(self):
        # Knowledge base with implication (adapted to disjunction)
        knowledge_base = [
            Clause([Literal("A", False), Literal("B")]),  # Not A or B (A implies B)
            Clause([Literal("A")]),  # A is true
        ]
        query = Clause([Literal("B")])  # Is B true?
        self.assertTrue(inference(knowledge_base, query))

    def test_inference_not_entailed(self):
        knowledge_base = [
            Clause([Literal("A", False), Literal("B")])  # Not A or B (A implies B)
        ]
        query = Clause([Literal("C")])  # Is C true?
        self.assertFalse(inference(knowledge_base, query))

    def test_resolution_multiple_complements(self):
        clause1 = Clause([Literal("A"), Literal("B"), Literal("C", False)])
        clause2 = Clause([Literal("A", False), Literal("B"), Literal("C")])
        expected_clause = Clause([Literal("B")])
        self.assertEqual(str(resolution(clause1, clause2)), str(expected_clause))

    def test_inference_complex(self):
        knowledge_base = [
            Clause([Literal("A", False), Literal("B")]),  # Not A or B
            Clause([Literal("B", False), Literal("C")]),  # Not B or C
            Clause([Literal("A")]),  # A is true
            Clause([Literal("D")]),  # D is true
        ]
        query = Clause([Literal("C")])  # Testing if C is true based on inference
        self.assertTrue(inference(knowledge_base, query))

    # Truth Table Function Edge Cases
    def test_truth_table_single_variable(self):
        formula = "A"
        expected_table = {
            (("A", True),): True,
            (("A", False),): False,
        }
        self.assertEqual(truth_table(formula), expected_table)

    def test_truth_table_nested_parentheses(self):
        formula = "((A AND B) OR (NOT C AND D))"
        variables = ["A", "B", "C", "D"]
        combinations = itertools.product([True, False], repeat=len(variables))
        expected_table = {}
        for combination in combinations:
            assignment = dict(zip(variables, combination))
            result = parse_formula(formula, assignment)
            key = tuple(sorted(assignment.items()))
            expected_table[key] = result

        actual_results = truth_table(formula)
        self.assertEqual(actual_results, expected_table)

    # Literal and Clause Representation Edge Cases
    def test_literal_positive_negative(self):
        literal1 = Literal("A")
        literal2 = Literal("A", positive=False)
        self.assertNotEqual(literal1, literal2)

    def test_clause_duplicate_literals(self):
        clause = Clause([Literal("A"), Literal("A", positive=False)])
        self.assertEqual(str(clause), "A v NOT A")

    # Resolution Function Edge Cases
    def test_resolution_no_complementary_literals(self):
        clause1 = Clause([Literal("A"), Literal("B")])
        clause2 = Clause([Literal("C"), Literal("D")])
        self.assertIsNone(resolution(clause1, clause2))

    def test_resolution_multiple_complementary_pairs(self):
        clause1 = Clause([Literal("A"), Literal("B", positive=False)])
        clause2 = Clause([Literal("A", positive=False), Literal("B")])
        resolved_clause = resolution(clause1, clause2)
        expected_clause = Clause(
            []
        )  # Empty clause because both complementary pairs are resolved
        self.assertEqual(resolved_clause, expected_clause)

    # Inference Engine Edge Cases
    def test_inference_unrelated_clauses(self):
        knowledge_base = [
            Clause([Literal("A")]),
            Clause([Literal("B")]),
        ]
        query = Clause([Literal("C")])  # C is unrelated
        self.assertFalse(inference(knowledge_base, query))

    def test_inference_negated_query_contradiction(self):
        knowledge_base = [
            Clause([Literal("A")]),
        ]
        query = Clause([Literal("A", positive=False)])  # Not A contradicts A
        self.assertTrue(inference(knowledge_base, query))


if __name__ == "__main__":
    unittest.main()
