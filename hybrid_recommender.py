import networkx as nx

from semantic_search import (
    get_similar_projects
)

from network_builder import G


# ---------------- HYBRID RECOMMENDER ----------------

def hybrid_recommendations(

    project_id,
    top_k=10
):

    # ---------------- SEMANTIC RESULTS ----------------

    semantic_results = get_similar_projects(

        project_id,
        top_k=20
    )

    scores = {}

    # ---------------- SEMANTIC SCORE ----------------

    for rank, project in enumerate(

        semantic_results
    ):

        pid = project["project_id"]

        semantic_score = (

            1 / (rank + 1)
        ) * 5

        scores[pid] = {

            "project": project,
            "score": semantic_score
        }

    # ---------------- GRAPH NODE ----------------

    target_node = None

    for node in G.nodes():

        if node.startswith("PROJECT::"):

            if str(project_id) in node:

                target_node = node
                break

    if not target_node:

        return semantic_results[:top_k]

    # ---------------- GRAPH NEIGHBORS ----------------

    neighbors = list(

        G.neighbors(target_node)
    )

    for neighbor in neighbors:

        second_neighbors = list(

            G.neighbors(neighbor)
        )

        for sn in second_neighbors:

            if not sn.startswith(

                "PROJECT::"
            ):

                continue

            if sn == target_node:

                continue

            # ---------------- EXTRACT PROJECT ----------------

            for project in semantic_results:

                project_title = (

                    f"PROJECT::{project['title']}"
                )

                if project_title == sn:

                    pid = project["project_id"]

                    if pid not in scores:

                        scores[pid] = {

                            "project": project,
                            "score": 0
                        }

                    scores[pid]["score"] += 3

    # ---------------- SORT ----------------

    ranked = sorted(

        scores.values(),

        key=lambda x: x["score"],

        reverse=True
    )

    return [

        r["project"]

        for r in ranked[:top_k]
    ]