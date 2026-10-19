from gen_epix.casedb.repositories.sa_model.case import TreeAlgorithm


def test_tree_algorithm_rank_column_uses_tree_algorithm_description() -> None:
    assert (
        TreeAlgorithm.__table__.c.rank.doc
        == "The rank of the tree algorithm, if relevant."
    )
