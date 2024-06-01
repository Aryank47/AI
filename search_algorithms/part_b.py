import random

from part_a import Search


def run_experiment(num_iterations, list_length, algorithm, print_details=True):
    """
    Runs an experiment using a given algorithm on a list of randomly generated numbers.

    Parameters:
    - num_iterations (int): The number of iterations to run the experiment.
    - list_length (int): The length of the list of random numbers.
    - algorithm (str): The name of the algorithm to use. Must be a valid algorithm name
                       in the Search class.
    - print_details (bool): If True, prints the list of numbers and the number of nodes explored
                           during each iteration. Defaults to False.

    Returns:
    - float: The average number of nodes explored during the num_iterations iterations.
    """
    random.seed(42)
    total_nodes_explored = 0

    for _ in range(num_iterations):
        random_numbers = [
            round(random.uniform(-300, 300), 2) for _ in range(list_length)
        ]
        search = Search(random_numbers)

        if algorithm == "hill_climbing_search":
            nodes_explored, _ = getattr(search, algorithm)
            nodes_explored = len(nodes_explored)
        else:
            visited_states, _ = getattr(search, algorithm)
            nodes_explored = len(visited_states)

        total_nodes_explored += nodes_explored

        if print_details:
            print(f"Input: {random_numbers}\tNodes Explored: {nodes_explored}")

    return total_nodes_explored / num_iterations


def main():
    """
    Runs the experiment for all algorithms and prints the results.
    """
    try:
        num_iterations = 25
        list_length = random.choice([3, 4, 5, 6])
        algorithms = [
            "breadth_first_search",
            "depth_first_search",
            "uniform_cost_search",
            "greedy_search",
            "a_star_search",
            "hill_climbing_search",
        ]

        for algorithm in algorithms:
            print("\n")
            print(
                f"Running {algorithm.replace('_', ' ').title()} Algorithm with list length {list_length} for a total of {num_iterations} iterations"
            )
            print(
                f"Average nodes explored: {run_experiment(num_iterations, list_length, algorithm)}"
            )

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
