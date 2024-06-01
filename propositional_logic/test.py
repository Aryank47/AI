import itertools
import unittest

from inference import inference, resolution
from literal_and_clause import Clause, Literal
from truth_table import eval_formula, truth_table


class TestPropositionalLogic(unittest.TestCase):
    def test_truth_table_simple(self):
        formula = "(A or B)"
        expected_table = {
            (("A", True), ("B", True), ("Formula", True)): True,
            (("A", True), ("B", False), ("Formula", True)): True,
            (("A", False), ("B", True), ("Formula", True)): True,
            (("A", False), ("B", False), ("Formula", False)): False,
        }
        self.assertEqual(truth_table(formula), expected_table)

    def test_truth_table_negation(self):
        formula = "not A"
        expected_table = {
            (("A", True), ("Formula", False)): False,
            (("A", False), ("Formula", True)): True,
        }
        self.assertEqual(truth_table(formula), expected_table)

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

    def test_truth_table_complex(self):
        formula = "(A and B) or (C and not D)"
        # Define the expected results for each combination
        variables = ["A", "B", "C", "D"]
        combinations = itertools.product([True, False], repeat=len(variables))
        expected_table = {}
        for combination in combinations:
            assignment = dict(zip(variables, combination))
            result = eval_formula(formula, assignment)
            key = tuple(sorted(assignment.items()) + [("Formula", result)])
            expected_table[key] = result

        actual_results = truth_table(formula)
        # Check that all expected keys and their corresponding results are correct
        for key, expected_result in expected_table.items():
            self.assertIn(key, actual_results)
            self.assertEqual(actual_results[key], expected_result)

    def test_resolution_multiple_complements(self):
        clause1 = Clause([Literal("A"), Literal("B"), Literal("C", False)])
        clause2 = Clause([Literal("A", False), Literal("B"), Literal("C")])
        # Expected to resolve on A, remaining B, C from clause1 and B, C from clause2, but C contradicts.
        expected_clause = Clause([Literal("B")])
        self.assertEqual(str(resolution(clause1, clause2)), str(expected_clause))

    def test_inference_complex(self):
        # A more complex knowledge base with multiple implications and facts
        knowledge_base = [
            Clause([Literal("A", False), Literal("B")]),  # Not A or B
            Clause([Literal("B", False), Literal("C")]),  # Not B or C
            Clause([Literal("A")]),  # A is true
            Clause([Literal("D")]),  # D is true
        ]
        query = Clause([Literal("C")])  # Testing if C is true based on inference
        self.assertTrue(inference(knowledge_base, query))


if __name__ == "__main__":
    unittest.main()
