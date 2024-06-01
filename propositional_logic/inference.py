from literal_and_clause import Clause, Literal

# def negate_clause(clause: Clause):
#     """Negates a clause, assuming the clause contains a single literal for simplicity."""
#     negated_literals = {Literal(lit.name, not lit.positive) for lit in clause.literals}
#     return Clause(negated_literals)


# def inference(knowledge_base: list[Clause], query: Clause, max_iterations=100):
#     # Negate the query
#     negated_query = negate_clause(query)

#     # Add the negated query to the knowledge base
#     clauses = knowledge_base.copy()
#     clauses.append(negated_query)

#     new = list(set(clauses))
#     for _ in range(max_iterations):
#         n = len(new)
#         pairs = [(new[i], new[j]) for i in range(n) for j in range(i + 1, n)]
#         for ci, cj in pairs:
#             resolvent = resolution(ci, cj)
#             if resolvent is not None:
#                 if not resolvent.literals:  # Empty clause found
#                     return True
#                 new.append(resolvent)

#         # If no new clauses were added
#         if len(new) == n:
#             break

#     return False


# # Extend to handle implications by converting them to disjunctions
# def handle_implications(clause: Clause):
#     """Convert implications in a clause to disjunctions using P -> Q equivalent to ~P or Q"""
#     updated_literals = set()
#     for lit in clause.literals:
#         if "->" in lit.name:  # Assuming the implication is represented like 'P->Q'
#             p, q = lit.name.split("->")
#             updated_literals.add(Literal(p, not lit.positive))
#             updated_literals.add(Literal(q, lit.positive))
#         else:
#             updated_literals.add(lit)
#     return Clause(updated_literals)


# # Example usage
# knowledge_base = [Clause([Literal("A"), Literal("B", False)]), Clause([Literal("B")])]
# query = Clause([Literal("A")])  # Query to check if 'A' is entailed by the KB

# # Convert any implications if present
# knowledge_base = [handle_implications(clause) for clause in knowledge_base]
# query = handle_implications(query)

# # Perform inference
# result = inference(knowledge_base, query)
# print(
#     "Query is entailed by the knowledge base:"
#     if result
#     else "Query is not entailed by the knowledge base."
# )


def resolution_old(clause1: Clause, clause2: Clause):
    literals1 = set(clause1.literals)
    literals2 = set(clause2.literals)
    new_literals = set()

    for lit in literals1:
        for lit2 in literals2:
            if lit.variable == lit2.variable and lit.positive != lit2.positive:
                # These are complementary literals, remove them
                temp_lit1 = literals1 - {lit}
                temp_lit2 = literals2 - {lit2}
                new_literals = temp_lit1.union(temp_lit2)
                if not new_literals:
                    return Clause([])
                return Clause(list(new_literals))
    # If no resolution occurs, return None or some indication
    return None


def inference(knowledge_base: list[Clause], query: Clause):
    # Negate the query
    negated_query = [Literal(lit.variable, not lit.positive) for lit in query.literals]
    clauses = knowledge_base + [Clause(negated_query)]
    new = set(clauses)
    while True:
        new_pairs = [(c1, c2) for c1 in new for c2 in new if c1 != c2]
        for c1, c2 in new_pairs:
            resolvent = resolution(c1, c2)
            if resolvent is not None:
                if not resolvent.literals:  # Empty clause
                    return True
                new.add(resolvent)
        if not new - set(clauses):  # No new clauses added
            break
        clauses.append(new)
    return False


def resolution(clause1: Clause, clause2: Clause):
    literals1 = set(clause1.literals)
    literals2 = set(clause2.literals)
    new_literals = literals1.union(literals2)

    resolved = False
    for lit1 in literals1:
        for lit2 in literals2:
            if lit1.variable == lit2.variable and lit1.positive != lit2.positive:
                resolved = True
                # Remove the complementary literals from the set
                new_literals.discard(lit1)
                new_literals.discard(lit2)

    if not resolved:
        return None  # Indicates no resolution occurred

    if not new_literals:  # Check for an empty clause which means a contradiction
        return Clause([])

    # Ensure no duplicate variables exist in the final clause
    final_literals = []
    seen_variables = set()
    for lit in new_literals:
        if lit.variable not in seen_variables:
            seen_variables.add(lit.variable)
            final_literals.append(lit)

    return Clause(final_literals)
