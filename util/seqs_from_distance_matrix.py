from typing import Any

import numpy as np
import scipy

TEST_DISTANCE_MATRIX = np.array(
    [
        [0.0, 1.0, 3.0, 2.0],
        [1.0, 0.0, 3.0, 3.0],
        [3.0, 3.0, 0.0, 0.0],
        [2.0, 3.0, 0.0, 0.0],
    ]
)


def main() -> None:
    seqs, optimize_result = generate_seqs_for_distance_matrix(TEST_DISTANCE_MATRIX)
    # Print the initial distance matrix
    print("\nInitial Distance Matrix:")
    print(optimize_result["initial_distance_matrix"])

    # Print the distance matrix generated from the tree
    print("\nDistance matrix derived from tree:")
    print(optimize_result["tree_distance_matrix"])

    # Print the distance matrix generated from the sequences
    print("\nDistance matrix derived from sequences:")
    print(optimize_result["seq_distance_matrix"])

    # Print the sequences
    print("\nSequences:")
    for seq in seqs:
        print(seq)


def generate_seqs_for_distance_matrix(
    distance_matrix: np.ndarray,
    alphabet: str = "acgt",
    linkage_method: str = "single",
    generation_method: str = "SUB_SEQ_PER_NODE",
    fractional_distance_multiplier: int = 1,
    **kwargs: dict,
) -> tuple[list[str], dict[str, Any | None] | None]:
    """
    Create a set of sequences from a distance matrix. The sequences are generated using
    a differential evolution algorithm.

    The return value is a tuple (seqs, optimize_result) where seqs is a list of sequences and
    optimize_result is a dictionary containing the initial distance matrix, the distance matrix
    derived from the tree, the distance matrix derived from the sequences, and the optimization
    result.
    """
    # Special case: zero or one sequences
    n_seqs = distance_matrix.shape[0]
    if n_seqs == 0:
        return [], None
    if n_seqs == 1:
        return [""], None

    # Create a distance matrix that is derived from the initial distance one and
    # exactly matches the hierarchical clustering tree derived from the latter, so that
    # a set of sequences is guaranteed to exist that exactly matches the resulting
    # distance matrix.
    condensed_distance_matrix = scipy.spatial.distance.squareform(distance_matrix)
    linkage_result = scipy.cluster.hierarchy.linkage(
        condensed_distance_matrix, linkage_method
    )
    int_linkage_result, distance_multiplier = _get_int_linkage_result(
        linkage_result, fractional_distance_multiplier
    )
    tree_distance_matrix = get_distance_matrix_from_linkage(int_linkage_result)

    # Derive a set of DNA sequences of length m and without indels whose hamming
    # distances correspond to the new distance matrix as much as possible
    if generation_method.upper() == "SUB_SEQ_PER_NODE":
        seqs, seq_optimize_result = generate_seqs_with_sub_seq_per_node(
            int_linkage_result, alphabet=alphabet, **kwargs  # type: ignore[arg-type]
        )
    elif generation_method.upper() == "DIFFERENTIAL_EVOLUTION":
        seqs, seq_optimize_result = generate_seqs_with_differential_evolution(
            tree_distance_matrix, alphabet=alphabet, **kwargs  # type: ignore[arg-type]
        )
    else:
        raise ValueError(
            "Invalid generation method. Use 'SUB_SEQ_PER_NODE' or 'DIFFERENTIAL_EVOLUTION'."
        )

    # Calculate the distance matrix from the sequences
    seq_distance_matrix = get_hamming_distance_matrix_from_aligned_seqs(seqs)

    # Create optimization result
    optimize_result: dict[str, Any | None] = {
        "initial_distance_matrix": distance_matrix,
        "tree_distance_matrix": tree_distance_matrix,
        "seq_distance_matrix": seq_distance_matrix,
        "seqs": seqs,
        "seq_optimize_result": seq_optimize_result,
        "linkage_method": linkage_method,
        "generation_method": generation_method,
        "distance_multiplier": distance_multiplier,
        "has_difference_between_tree_and_seq_distance_matrix": np.any(
            (tree_distance_matrix - distance_multiplier * distance_matrix) != 0
        ),
        "has_difference_between_tree_and_seq_distance_matrix": np.any(
            np.abs(tree_distance_matrix - seq_distance_matrix) > 0
        ),
    }
    return seqs, optimize_result


def get_distance_matrix_from_linkage(linkage_result: np.ndarray) -> np.ndarray:
    """
    Derive all pairwise distances between leafs from the linkage result.
    """
    n_seqs = len(linkage_result) + 1

    # Initialise distance matrix and leaves per cluster (clusters 1:n are the leaves,
    # the linkage_result describes clusters n+1:2n-1)
    distance_matrix = np.zeros((n_seqs, n_seqs))
    cluster_leaves: list[list[int]] = [list()] * (2 * n_seqs - 1)
    for i in range(n_seqs):
        cluster_leaves[i] = [i]

    # For each cluster in the linkage result, add the distances between the two clusters
    for cluster_id, cluster_data in enumerate(linkage_result):
        # cluster_data[0] = first child cluster_id
        # cluster_data[1] = second child cluster_id
        # cluster_data[2] = distance between child clusters
        # cluster_data[3] = number of leaves in the cluster

        # add the distances between the two clusters to the distance matrix
        leaves1 = cluster_leaves[int(cluster_data[0])]
        leaves2 = cluster_leaves[int(cluster_data[1])]
        cluster_leaves[n_seqs + cluster_id] = leaves1 + leaves2
        distance = cluster_data[2]
        for leaf1 in leaves1:
            distance_matrix[leaf1][leaves2] += distance
        for leaf2 in leaves2:
            distance_matrix[leaf2][leaves1] += distance

    return distance_matrix


def generate_seqs_with_sub_seq_per_node(
    int_linkage_result: np.ndarray,
    alphabet: str = "acgt",
    fractional_distance_multiplier: int = 1,
    **kwargs: dict,
) -> tuple[list[str], Any | None]:
    """
    Generate a set of (DNA) sequences of length m and without indels whose hamming
    distances correspond to the new distance matrix as much as possible.
    """
    # Parse arguments
    if len(alphabet) < 3:
        raise ValueError("Alphabet must contain at least 3 characters")
    n_seqs = len(int_linkage_result) + 1

    # Special case: zero or one sequences
    if n_seqs == 0:
        return [], None
    if n_seqs == 1:
        return [alphabet[0]], None

    # Initialise some
    node_leaves: list = [None] * (2 * n_seqs - 1)
    node_heights: list = [0] * (2 * n_seqs - 1)
    for i in range(n_seqs):
        node_leaves[i] = {i}

    # For each cluster in the linkage result, add the distances between the two clusters
    # as a seq snippet with length equal to the distance
    seqs_per_node: list[list[str]] = [list() for _ in range(n_seqs)]
    all_leaves = set(range(n_seqs))
    for i, node_data in enumerate(int_linkage_result):
        # node_data[0] = first child node id
        # node_data[1] = second child node id
        # node_data[2] = distance between child nodes
        # node_data[3] = number of leaves in the node

        # Unpack node data
        child_node_id1 = int(node_data[0])
        child_node_id2 = int(node_data[1])
        child_leaves1 = node_leaves[child_node_id1]
        child_leaves2 = node_leaves[child_node_id2]
        node_id = n_seqs + i
        distance = node_data[2]
        node_leaves[node_id] = set.union(child_leaves1, child_leaves2)
        node_heights[node_id] = distance
        # Add the distances between the two clusters and with all the other leaves to
        # the sequences, a seq snippet with length equal to the distance:
        # For the first and second child node leaves, add a seq made of the first and
        # second alphabet characters, respectively. For all other leaves, add a seq
        # made of the third alphabet character. As such all other leaves also have the
        # distance to the first and second child node leaves added, but not among each
        # other.
        distance_to_add = distance - max(
            node_heights[child_node_id1], node_heights[child_node_id2]
        )
        seq1 = [alphabet[0] for _ in range(distance_to_add)]
        seq2 = [alphabet[1] for _ in range(distance_to_add)]
        seq3 = [alphabet[2] for _ in range(distance_to_add)]
        for leaf in child_leaves1:
            seqs_per_node[leaf].extend(seq1)
        for leaf in child_leaves2:
            seqs_per_node[leaf].extend(seq2)
        for leaf in all_leaves - child_leaves1 - child_leaves2:
            seqs_per_node[leaf].extend(seq3)

    # Convert to seqs using alphabet
    seqs = ["".join(x) for x in seqs_per_node]

    return seqs, None


def generate_seqs_with_differential_evolution(
    tree_distance_matrix: np.ndarray,
    alphabet: str = "acgt",
    seq_length: int | None = None,
    **kwargs: dict,
) -> tuple[list[str], Any | None]:
    """
    Generate a set of (DNA) sequences of length m and without indels whose hamming
    distances correspond to the new distance matrix as much as possible. Scipy's
    differential evolution algorithm is used to optimize the sequences.
    """
    # Parse arguments
    if not seq_length:
        # If no seq_length is provided, use the maximum distance between any two
        # sequences as the length of the sequences
        seq_length = int(np.ceil(np.max(tree_distance_matrix)))
    strategy = kwargs.get("strategy", "best1bin")
    maxiter = kwargs.get("maxiter", 1000)
    popsize = kwargs.get("popsize", 15)
    tol = kwargs.get("tol", 0.01)
    n_seqs = tree_distance_matrix.shape[0]

    # Special case: zero or one sequences
    if n_seqs == 0:
        return [], None
    if n_seqs == 1:
        return [alphabet[0] * seq_length], None

    # Special case: two sequences
    if n_seqs == 2:
        return [alphabet[0] * seq_length, alphabet[1] * seq_length], None

    # Optimize using differential evolution
    optimize_result = scipy.optimize.differential_evolution(
        objective_function,
        bounds=[
            (0, len(alphabet) - 0.5) for _ in range(n_seqs * seq_length)
        ],  # Subtract 0.5 to make the upper bound with certainty exclusive (potentially a bug in scipy for integer bounds)
        args=(n_seqs, tree_distance_matrix),
        strategy=strategy,
        maxiter=maxiter,
        popsize=popsize,
        tol=tol,
        integrality=np.array([True for i in range(n_seqs * seq_length)]),
    )

    # Convert optimize_result to a list of sequences
    seqs = []
    chromosome = [int(x) for x in optimize_result.x]
    for i in range(n_seqs):
        seqs.append(
            "".join(
                [
                    alphabet[chromosome[j]]
                    for j in range(i * seq_length, (i + 1) * seq_length)
                ]
            )
        )

    return seqs, optimize_result


def get_hamming_distance_matrix_from_aligned_seqs(seqs: list[str]) -> np.ndarray:
    """
    Calculate the hamming distance matrix from a list of aligned sequences.
    The sequences are assumed to be aligned and therefore of the same length.
    """
    n_seqs = len(seqs)
    # Specal case: zero or one sequences
    if n_seqs == 0:
        return np.array([])
    if n_seqs == 1:
        return np.array([[0]])

    # Go over all pairs of sequences and calculate the hamming distance
    # n_positions = len(seqs[0])
    distance_matrix = np.zeros((n_seqs, n_seqs))
    encoded_seqs = [np.frombuffer(x.encode("ascii"), dtype=np.int8) for x in seqs]
    for i in range(n_seqs - 1):
        # seq1 = seqs[i]
        seq1 = encoded_seqs[i]
        for j in range(i + 1, n_seqs):
            # seq2 = seqs[j]
            seq2 = encoded_seqs[j]
            # Calculate the hamming distance between seq1 and seq2
            # Less efficient:
            # distance = sum(
            #     1 for k in range(n_positions) if seq1[k] != seq2[k]
            # )
            # Using sequences encoded as ndarrays:
            distance = np.count_nonzero(seq1 != seq2)
            # Add the distance to the distance matrix
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance

    return distance_matrix


def objective_function(
    chromosome: np.ndarray, n_seqs: int, target_distance_matrix: np.ndarray
) -> float:
    """
    Objective function for the optimization algorithm. The function calculates the
    energy of the current chromosome. The energy is calculated as the sum of the
    absolute differences between the target distance matrix and the distance matrix
    derived from the chromosome. The chromosome is a flat array of integers
    representing the concatenated DNA sequences.
    """
    energy = 0.0
    # Calculate the pairwise hamming distances
    seq_length = int(len(chromosome) / n_seqs)
    for i in range(n_seqs - 1):
        seq1 = chromosome[i * seq_length : (i + 1) * seq_length]
        for j in range(i + 1, n_seqs):
            # Calculate the hamming distance between seqs[i] and seqs[j]
            seq2 = chromosome[j * seq_length : (j + 1) * seq_length]
            seq_distance = np.sum(seq1 != seq2)
            # Add the difference between the target distance and the calculated
            # distance to the energy
            energy += np.abs(target_distance_matrix[i][j] - seq_distance)
    return energy


def _get_int_linkage_result(
    linkage_result: np.ndarray, fractional_distance_multiplier: int
) -> tuple[np.ndarray, int]:
    is_fractional = any(linkage_result[:, 2] % 1 != 0)
    distance_multiplier = fractional_distance_multiplier
    if is_fractional and fractional_distance_multiplier != 1:
        int_linkage_result = np.copy(linkage_result)
        int_linkage_result[:, 2] = np.round(
            linkage_result[:, 2] * fractional_distance_multiplier
        )
        int_linkage_result = int_linkage_result.astype(int)
    else:
        distance_multiplier = 1
        int_linkage_result = linkage_result.astype(int)
    return int_linkage_result, distance_multiplier
