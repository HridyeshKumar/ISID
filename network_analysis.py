import networkx as nx
import matplotlib.pyplot as plt
from network_builder import G


# ---------------- GRAPH ANALYTICS ----------------

print("\n🚀 GRAPH ANALYTICS\n")


# ---------------- BASIC STATS ----------------

print(
    "📊 Total Nodes:",
    G.number_of_nodes()
)

print(
    "🔗 Total Edges:",
    G.number_of_edges()
)


# ---------------- DEGREE CENTRALITY ----------------

degree_centrality = nx.degree_centrality(G)

top_degree = sorted(

    degree_centrality.items(),

    key=lambda x: x[1],

    reverse=True
)[:10]


print("\n🔥 TOP CONNECTED NODES\n")

for node, score in top_degree:

    print(
        f"{node} -> {round(score, 4)}"
    )


# ---------------- BETWEENNESS CENTRALITY ----------------

betweenness = nx.betweenness_centrality(

    G,

    k=min(100, len(G.nodes()))
)

top_bridges = sorted(

    betweenness.items(),

    key=lambda x: x[1],

    reverse=True
)[:10]


print("\n🌉 TOP BRIDGE NODES\n")

for node, score in top_bridges:

    print(
        f"{node} -> {round(score, 4)}"
    )


# ---------------- PAGERANK ----------------

pagerank = nx.pagerank(G)

top_pagerank = sorted(

    pagerank.items(),

    key=lambda x: x[1],

    reverse=True
)[:10]


print("\n⭐ MOST INFLUENTIAL NODES\n")

for node, score in top_pagerank:

    print(
        f"{node} -> {round(score, 4)}"
    )


# ---------------- COMMUNITY DETECTION ----------------

communities = nx.community.greedy_modularity_communities(G)

print(
    "\n🧩 TOTAL COMMUNITIES:",
    len(communities)
)

print("\n📌 SAMPLE COMMUNITIES\n")

for i, community in enumerate(communities[:5]):

    sample_nodes = list(community)[:5]

    print(
        f"Community {i+1}:"
    )

    print(sample_nodes)

    print()


# ---------------- VISUALIZATION ----------------

plt.figure(figsize=(18, 12))


# ---------------- LAYOUT ----------------

pos = nx.spring_layout(

    G,

    k=0.4,

    iterations=50
)


# ---------------- NODE COLORS ----------------

node_colors = []

for node in G.nodes():

    if node.startswith("PROJECT::"):

        node_colors.append("skyblue")

    elif node.startswith("ACTOR::"):

        node_colors.append("orange")

    elif node.startswith("LOCATION::"):

        node_colors.append("lightgreen")

    elif node.startswith("TOPIC::"):

        node_colors.append("pink")

    else:

        node_colors.append("gray")


# ---------------- NODE SIZES ----------------

node_sizes = []

for node in G.nodes():

    size = degree_centrality.get(
        node,
        0
    ) * 10000

    node_sizes.append(
        max(size, 50)
    )


# ---------------- DRAW GRAPH ----------------

nx.draw(

    G,

    pos,

    with_labels=False,

    node_size=node_sizes,

    edge_color="gray",

    node_color=node_colors,

    alpha=0.7
)


# ---------------- TITLE ----------------

plt.title(

    "ISID Ecosystem Intelligence Analytics",

    fontsize=18
)


# ---------------- SHOW ----------------

plt.show()