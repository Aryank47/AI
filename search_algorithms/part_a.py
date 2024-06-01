import heapq
from queue import Queue


class Search:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.goal_state = sorted(initial_state.copy())
        self.state_length = len(initial_state)

    def print_visited_states(self, visited_states, prefix="State"):
        print("-- Visited States --")
        print(f"Total states explored: {len(visited_states)}")
        for i, state in enumerate(visited_states):
            print(f"{prefix} {i} -> {state}")

    def print_final_path(self, visited_states, path, prefix="State"):
        print("-- Solution Path --")
        print(f"Length of solution path: {len(path)}")
        for i, state in enumerate(path):
            visited_index = visited_states.index(state)
            print(f"{prefix} {visited_index} -> {state}")

    def inversion_heuristic(self, state):
        return sum(
            1
            for i in range(len(state))
            for j in range(i + 1, len(state))
            if state[i] > state[j]
        )

    def misplaced_tiles_heuristic(self, state):
        return sum(
            1 for i in range(self.state_length) if state[i] != self.goal_state[i]
        )

    def absolute_difference_heuristic(self, state):
        return sum(abs(state[i] - self.goal_state[i]) for i in range(self.state_length))

    def successors(self, state):
        return [
            state[:i] + state[i + 1 : i + 2] + state[i : i + 1] + state[i + 2 :]
            for i in range(self.state_length - 1)
        ]

    def misplaced_elements_cost(self, state):
        return sum(
            1 for i in range(self.state_length) if self.initial_state[i] != state[i]
        )

    @property
    def breadth_first_search(self):
        queue = Queue()
        queue.put((self.initial_state, [tuple(self.initial_state)]))
        visited_states = []

        while not queue.empty():
            state, path = queue.get()
            if tuple(state) in visited_states:
                continue
            visited_states.append(tuple(state))

            if state == self.goal_state:
                return visited_states, path

            for successor in self.successors(state.copy()):
                new_path = path + [tuple(successor)]
                queue.put((successor, new_path))

        return None

    @property
    def depth_first_search(self):
        stack = []
        stack.append((self.initial_state, [tuple(self.initial_state)]))
        visited_states = []

        while stack:
            state, path = stack.pop()
            if tuple(state) in visited_states:
                continue
            visited_states.append(tuple(state))

            if state == self.goal_state:
                return visited_states, path

            for successor in self.successors(state.copy()):
                new_path = path + [tuple(successor)]
                stack.append((successor, new_path))

        return None

    @property
    def uniform_cost_search(self):
        heap = [(0, self.initial_state, [tuple(self.initial_state)])]
        visited_states = []

        while heap:
            cost, state, path = heapq.heappop(heap)
            if tuple(state) in visited_states:
                continue
            visited_states.append(tuple(state))

            if state == self.goal_state:
                return visited_states, path

            for successor in self.successors(state.copy()):
                new_cost = self.misplaced_elements_cost(successor)
                new_path = path + [tuple(successor)]
                heapq.heappush(heap, (new_cost, successor, new_path))

        return None

    @property
    def greedy_search(self):
        heap = [
            (
                self.absolute_difference_heuristic(self.initial_state),
                self.initial_state,
                [tuple(self.initial_state)],
            )
        ]
        visited_states = []

        while heap:
            _, state, path = heapq.heappop(heap)
            if tuple(state) in visited_states:
                continue
            visited_states.append(tuple(state))

            if state == self.goal_state:
                return visited_states, path

            for successor in self.successors(state.copy()):
                new_path = path + [tuple(successor)]
                heapq.heappush(
                    heap,
                    (
                        self.absolute_difference_heuristic(successor),
                        successor,
                        new_path,
                    ),
                )

        return None

    @property
    def a_star_search(self):
        heap = [
            (
                self.absolute_difference_heuristic(self.initial_state),
                0,
                self.initial_state,
                [tuple(self.initial_state)],
            )
        ]
        visited_states = []

        while heap:
            _, cost, state, path = heapq.heappop(heap)
            if tuple(state) in visited_states:
                continue
            visited_states.append(tuple(state))

            if state == self.goal_state:
                return visited_states, path

            for successor in self.successors(state.copy()):
                new_cost = self.misplaced_elements_cost(successor)
                new_path = path + [tuple(successor)]
                heapq.heappush(
                    heap,
                    (
                        self.absolute_difference_heuristic(successor) + new_cost,
                        new_cost,
                        successor,
                        new_path,
                    ),
                )

        return None

    @property
    def hill_climbing_search(self):
        current_state = self.initial_state.copy()
        nodes_explored = 0

        while True:
            h = self.inversion_heuristic(current_state)
            if h == 0:
                return current_state, nodes_explored

            neighbors = self.successors(current_state.copy())
            nodes_explored += len(neighbors)

            best_neighbor = min(neighbors, key=self.inversion_heuristic)
            if self.inversion_heuristic(best_neighbor) >= h:
                return current_state, nodes_explored

            current_state = best_neighbor


def main():
    try:
        user_input = input("Enter the numbers in the format 'n 1 2 3 ...n': ")
        input_list = user_input.split()
        array = list(map(float, input_list[1:]))

        problem_solver = Search(array)

        print("\nLength of Array ->", len(array))
        print("Array ->", array)

        for algorithm in [
            "breadth_first_search",
            "depth_first_search",
            "uniform_cost_search",
            "greedy_search",
            "a_star_search",
            "hill_climbing_search",
        ]:
            print(f"\n{algorithm.capitalize().replace('_', ' ')} Output\n")
            visited_states, path = getattr(problem_solver, algorithm)

            if algorithm == "hill_climbing_search":
                print(f"Final State -> {visited_states}, Nodes Explored -> {path}")
                problem_solver.print_visited_states(visited_states)
            else:
                problem_solver.print_final_path(visited_states, path)
                problem_solver.print_visited_states(visited_states)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
