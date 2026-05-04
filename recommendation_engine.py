from semantic_search import get_similar_projects


# =========================================================
# RECOMMEND PROJECTS
# =========================================================

def recommend_projects(project_id, top_k=5):

    try:

        recommendations = get_similar_projects(

            project_id,

            top_k=top_k
        )

        results = []

        for r in recommendations:

            results.append({

                "project": r,

                "score": r.get(
                    "impact_score",
                    0
                )
            })

        return results

    except Exception as e:

        print(

            "Recommendation Error:",

            e
        )

        return []


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    results = recommend_projects(1)

    print("\n🚀 RECOMMENDATIONS\n")

    for item in results:

        project = item["project"]

        print(

            "📌",

            project["title"]
        )

        print(

            "⭐ Score:",

            item["score"]
        )

        print()