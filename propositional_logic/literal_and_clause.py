# class Literal:
#     def __init__(self, name, positive=True):
#         self.name = name
#         self.positive = positive

#     def is_complement(self, other):
#         return self.name == other.name and self.positive != other.positive

#     def __str__(self):
#         if self.positive:
#             return self.name
#         else:
#             return f"NOT {self.name}"

#     def __repr__(self):
#         return self.__str__()

#     def __eq__(self, other):
#         return self.name == other.name and self.positive == other.positive

#     def __hash__(self):
#         return hash((self.name, self.positive))


# class Clause:
#     def __init__(self, literals=None):
#         if literals is None:
#             literals = []
#         self.literals = set(literals)  # Using a set to avoid duplicates

#     def add_literal(self, literal):
#         self.literals.add(literal)

#     def __str__(self):
#         if not self.literals:
#             return "Empty Clause"
#         return " OR ".join(str(literal) for literal in self.literals)

#     def __repr__(self):
#         return self.__str__()


# def resolution(clause1, clause2):
#     new_literals = clause1.literals.union(clause2.literals)
#     resolved = False

#     for literal1 in clause1.literals:
#         for literal2 in clause2.literals:
#             if literal1.is_complement(literal2):
#                 # If complementary literals found, remove both and mark as resolved
#                 new_literals.discard(literal1)
#                 new_literals.discard(literal2)
#                 resolved = True

#     if resolved:
#         # Return new Clause with the remaining literals after removing the complements
#         return Clause(new_literals)
#     else:
#         # If no resolution possible, return None or an appropriate result
#         return None


class Literal:
    def __init__(self, variable, positive=True):
        self.variable = variable
        self.positive = positive

    def __str__(self):
        if not self.positive:
            return f"not {self.variable}"
        return self.variable

    def __eq__(self, other: "Literal"):
        return self.variable == other.variable and self.positive == other.positive

    def __hash__(self):
        return hash((self.variable, self.positive))


class Clause:
    def __init__(self, literals: list[Literal]):
        self.literals = literals

    def __str__(self):
        return " v ".join(str(lit) for lit in self.literals)
