import itertools
import re
import unittest
from typing import Dict, List, Optional, Tuple


class FormulaEvaluator:
    """Responsible for parsing and evaluating logical formulas."""

    @staticmethod
    def parse_formula(formula: str, assignment: Dict[str, bool]) -> bool:
        formula = (
            formula.replace("AND", "and")
            .replace("OR", "or")
            .replace("NOT", "not")
            .replace(
                "->", " or not "
            )  # Implication: P -> Q is equivalent to not P or Q
        )
        try:
            return eval(formula, {"__builtins__": None}, assignment.copy())
        except Exception as e:
            raise ValueError("Invalid formula.") from e


class TruthTable:
    """Generates truth tables for logical formulas."""

    def __init__(self, formula: str):
        self.formula = formula
        self.variables = sorted(set(re.findall(r"\b[A-Z]\b", formula)))

    def generate(self) -> Dict[Tuple[str, bool], bool]:
        combinations = itertools.product([True, False], repeat=len(self.variables))
        results = {}
        for combination in combinations:
            assignment = dict(zip(self.variables, combination))
            result = FormulaEvaluator.parse_formula(self.formula, assignment)
            key = tuple((var, assignment[var]) for var in self.variables)
            results[key] = result
        return results


class Literal:
    """Represents a logical literal."""

    def __init__(self, variable: str, positive: bool = True):
        self.variable = variable
        self.positive = positive

    def __str__(self):
        return f"{'' if self.positive else 'NOT '}{self.variable}"

    def __eq__(self, other):
        return (
            isinstance(other, Literal)
            and self.variable == other.variable
            and self.positive == other.positive
        )

    def __hash__(self):
        return hash((self.variable, self.positive))


class Clause:
    """Represents a disjunction (OR) of literals."""

    def __init__(self, literals: List[Literal]):
        self.literals = literals

    def __str__(self):
        return " v ".join(str(lit) for lit in self.literals)

    def __eq__(self, other):
        return isinstance(other, Clause) and set(self.literals) == set(other.literals)

    def __hash__(self):
        return hash(tuple(sorted(self.literals, key=lambda lit: lit.variable)))


class Resolution:
    """Provides methods for resolving logical clauses."""

    @staticmethod
    def resolve(clause1: Clause, clause2: Clause) -> Optional[Clause]:
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


class InferenceEngine:
    """Implements a resolution-based inference engine that handles implication logic."""

    def __init__(self, knowledge_base: List[Clause], max_iterations: int = 100):
        self.knowledge_base = self.preprocess_clauses(knowledge_base)
        self.max_iterations = max_iterations

    def preprocess_clauses(self, clauses: List[Clause]) -> List[Clause]:
        """Convert implications in clauses to disjunctions."""
        processed_clauses = []
        for clause in clauses:
            processed_literals = []
            for lit in clause.literals:
                # If a clause represents an implication, transform it into its disjunction
                if " -> " in lit.variable:

                    # Create literals for `¬A` and `B`
                    antecedent, consequent = lit.variable.split("->")
                    processed_literals.append(
                        Literal(antecedent.strip(), positive=False)
                    )
                    processed_literals.append(
                        Literal(consequent.strip(), positive=True)
                    )
                else:
                    processed_literals.append(lit)
            processed_clauses.append(Clause(processed_literals))
        return processed_clauses

    def preprocess_query(self, query: Clause) -> Clause:
        """Convert implications in the query to disjunctions."""
        return self.preprocess_clauses([query])[0]

    def is_entailed(self, query: Clause) -> bool:
        query = self.preprocess_query(query)
        negated_query = negated_query = Clause(
            [Literal(lit.variable, not lit.positive) for lit in query.literals]
        )

        # Check for contradiction in the knowledge base
        if negated_query in self.knowledge_base:
            return True

        clauses = set(self.knowledge_base + [negated_query])
        new_clauses = set()

        for _ in range(self.max_iterations):
            pairs = [(c1, c2) for c1 in clauses for c2 in clauses if c1 != c2]
            for c1, c2 in pairs:
                resolvent = Resolution.resolve(c1, c2)
                if resolvent is not None:
                    if resolvent and not resolvent.literals:
                        return True
                    if resolvent:
                        new_clauses.add(resolvent)

            if not new_clauses - clauses:
                break
            clauses.update(new_clauses)
            new_clauses.clear()

        return False


class TestPropositionalLogic(unittest.TestCase):

    # # Truth Table Function Edge Cases
    # def test_truth_table_single_variable(self):
    #     formula = "A"
    #     expected_table = {
    #         (("A", True),): True,
    #         (("A", False),): False,
    #     }
    #     truth_table = TruthTable(formula)
    #     self.assertEqual(truth_table.generate(), expected_table)

    # def test_truth_table_nested_parentheses(self):
    #     formula = "((A AND B) OR (NOT C AND D))"
    #     variables = ["A", "B", "C", "D"]
    #     combinations = itertools.product([True, False], repeat=len(variables))
    #     expected_table = {}
    #     for combination in combinations:
    #         assignment = dict(zip(variables, combination))
    #         result = FormulaEvaluator.parse_formula(formula, assignment)
    #         key = tuple(sorted(assignment.items()))
    #         expected_table[key] = result

    #     truth_table = TruthTable(formula)
    #     actual_results = truth_table.generate()
    #     self.assertEqual(actual_results, expected_table)

    # # Literal and Clause Representation Edge Cases
    # def test_literal_positive_negative(self):
    #     literal1 = Literal("A")
    #     literal2 = Literal("A", positive=False)
    #     self.assertNotEqual(literal1, literal2)

    # def test_clause_duplicate_literals(self):
    #     clause = Clause([Literal("A"), Literal("A", positive=False)])
    #     self.assertEqual(str(clause), "A v NOT A")

    # # Resolution Function Edge Cases
    # def test_resolution_no_complementary_literals(self):
    #     clause1 = Clause([Literal("A"), Literal("B")])
    #     clause2 = Clause([Literal("C"), Literal("D")])
    #     self.assertIsNone(Resolution.resolve(clause1, clause2))

    # def test_resolution_multiple_complementary_pairs(self):
    #     clause1 = Clause([Literal("A"), Literal("B", positive=False)])
    #     clause2 = Clause([Literal("A", positive=False), Literal("B")])
    #     resolved_clause = Resolution.resolve(clause1, clause2)
    #     expected_clause = Clause(
    #         []
    #     )  # Empty clause because both complementary pairs are resolved
    #     self.assertEqual(resolved_clause, expected_clause)

    # # Inference Engine Edge Cases
    # def test_inference_unrelated_clauses(self):
    #     knowledge_base = [
    #         Clause([Literal("A")]),
    #         Clause([Literal("B")]),
    #     ]
    #     query = Clause([Literal("C")])  # C is unrelated
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertFalse(inference_engine.is_entailed(query))

    # def test_inference_negated_query_contradiction(self):
    #     knowledge_base = [
    #         Clause([Literal("A")]),
    #     ]
    #     query = Clause([Literal("A", positive=False)])  # Not A contradicts A
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertTrue(inference_engine.is_entailed(query))

    # # Additional test cases for original scenarios
    # def test_truth_table_simple(self):
    #     formula = "(A OR B)"
    #     expected_table = {
    #         (("A", True), ("B", True)): True,
    #         (("A", True), ("B", False)): True,
    #         (("A", False), ("B", True)): True,
    #         (("A", False), ("B", False)): False,
    #     }
    #     truth_table = TruthTable(formula)
    #     self.assertEqual(truth_table.generate(), expected_table)

    # def test_truth_table_negation(self):
    #     formula = "NOT A"
    #     expected_table = {(("A", True),): False, (("A", False),): True}
    #     truth_table = TruthTable(formula)
    #     self.assertEqual(truth_table.generate(), expected_table)

    # def test_truth_table_complex(self):
    #     formula = "(A AND B) OR (C AND NOT D)"
    #     variables = ["A", "B", "C", "D"]
    #     combinations = itertools.product([True, False], repeat=(len(variables)))
    #     expected_table = {}
    #     for combination in combinations:
    #         assignment = dict(zip(variables, combination))
    #         result = FormulaEvaluator.parse_formula(formula, assignment)
    #         key = tuple(sorted(assignment.items()))
    #         expected_table[key] = result

    #     truth_table = TruthTable(formula)
    #     actual_results = truth_table.generate()
    #     self.assertEqual(actual_results, expected_table)

    # def test_resolution_contradiction(self):
    #     clause1 = Clause([Literal("A")])
    #     clause2 = Clause([Literal("A", positive=False)])
    #     expected_clause = Clause([])
    #     self.assertEqual(Resolution.resolve(clause1, clause2), expected_clause)

    # def test_resolution_no_contradiction(self):
    #     clause1 = Clause([Literal("A"), Literal("B")])
    #     clause2 = Clause([Literal("C"), Literal("D")])
    #     expected_clause = None  # Expecting None since no resolution should occur
    #     self.assertEqual(Resolution.resolve(clause1, clause2), expected_clause)

    # def test_inference_entailment(self):
    #     knowledge_base = [
    #         Clause(
    #             [Literal("A", positive=False), Literal("B")]
    #         ),  # Not A or B (A implies B)
    #         Clause([Literal("A")]),  # A is true
    #     ]
    #     query = Clause([Literal("B")])  # Is B true?
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertTrue(inference_engine.is_entailed(query))

    # def test_inference_not_entailed(self):
    #     knowledge_base = [
    #         Clause(
    #             [Literal("A", positive=False), Literal("B")]
    #         )  # Not A or B (A implies B)
    #     ]
    #     query = Clause([Literal("C")])  # Is C true?
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertFalse(inference_engine.is_entailed(query))

    # def test_inference_complex(self):
    #     knowledge_base = [
    #         Clause([Literal("A", positive=False), Literal("B")]),  # Not A or B
    #         Clause([Literal("B", positive=False), Literal("C")]),  # Not B or C
    #         Clause([Literal("A")]),  # A is true
    #         Clause([Literal("D")]),  # D is true
    #     ]
    #     query = Clause([Literal("C")])  # Testing if C is true based on inference
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertTrue(inference_engine.is_entailed(query))

    # def test_resolution_multiple_complements(self):
    #     clause1 = Clause([Literal("A"), Literal("B"), Literal("C", False)])
    #     clause2 = Clause([Literal("A", False), Literal("B"), Literal("C")])
    #     expected_clause = Clause([Literal("B")])
    #     self.assertEqual(
    #         str(Resolution.resolve(clause1, clause2)), str(expected_clause)
    #     )

    # #####################################################################

    # def test_implication_in_knowledge_base(self):
    #     # A implies B (A -> B) is equivalent to Not A or B
    #     knowledge_base = [
    #         Clause([Literal("A -> B")]),
    #         Clause([Literal("A")]),
    #     ]  # Not A or B
    #     query = Clause([Literal("B")])  # Is B true?
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertTrue(inference_engine.is_entailed(query))

    # def test_implication_with_multiple_clauses(self):
    #     # A implies B (A -> B) and B implies C (B -> C)
    #     knowledge_base = [
    #         Clause([Literal("A -> B")]),  # Not A or B
    #         Clause([Literal("B -> C")]),  # Not B or C
    #         Clause([Literal("A")]),
    #         Clause([Literal("B")]),
    #     ]
    #     query = Clause([Literal("C")])  # Is C true?
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertTrue(inference_engine.is_entailed(query))

    # def test_implication_with_negated_query(self):
    #     knowledge_base = [Clause([Literal("A -> B")])]
    #     query = Clause([Literal("A")])  # Is A true?
    #     inference_engine = InferenceEngine(knowledge_base)
    #     self.assertFalse(inference_engine.is_entailed(query))

    # def test_implication_not_entailed(self):
    # knowledge_base = [Clause([Literal("A -> B")])]
    # query = Clause([Literal("C")])  # Is C true?
    # inference_engine = InferenceEngine(knowledge_base)
    # self.assertFalse(inference_engine.is_entailed(query))

    def test_empty_formula(self):
        with self.assertRaises(ValueError):
            TruthTable("").generate()

    def test_unknown_variable(self):
        formula = "A AND X"
        with self.assertRaises(ValueError):
            TruthTable(formula).generate()

    def test_unknown_operator(self):
        formula = "A XOR B"
        with self.assertRaises(ValueError):
            TruthTable(formula).generate()

    def test_literal_case_insensitive(self):
        literal1 = Literal("A")
        literal2 = Literal("a")
        self.assertNotEqual(literal1, literal2)

    def test_empty_clause(self):
        clause = Clause([])
        self.assertEqual(str(clause), "")

    def test_identical_clauses(self):
        clause = Clause([Literal("A"), Literal("B")])
        self.assertIsNone(Resolution.resolve(clause, clause))

    def test_partial_complementary_pairs(self):
        clause1 = Clause([Literal("A"), Literal("B"), Literal("C", False)])
        clause2 = Clause([Literal("B"), Literal("C")])
        expected_clause = Clause([Literal("B")])
        self.assertEqual(
            str(Resolution.resolve(clause1, clause2)), str(expected_clause)
        )

    def test_empty_knowledge_base(self):
        inference_engine = InferenceEngine([])
        query = Clause([Literal("A")])
        self.assertFalse(inference_engine.is_entailed(query))

    def test_empty_query(self):
        knowledge_base = [Clause([Literal("A")])]
        query = Clause([])
        inference_engine = InferenceEngine(knowledge_base)
        self.assertFalse(inference_engine.is_entailed(query))

    def test_invalid_query_type(self):
        knowledge_base = [Clause([Literal("A")])]
        inference_engine = InferenceEngine(knowledge_base)
        with self.assertRaises(ValueError):
            inference_engine.is_entailed("A")

    def test_no_new_clauses_generated(self):
        knowledge_base = [Clause([Literal("A")]), Clause([Literal("B")])]
        query = Clause([Literal("C")])
        inference_engine = InferenceEngine(knowledge_base)
        self.assertFalse(inference_engine.is_entailed(query))


if __name__ == "__main__":
    unittest.main()
