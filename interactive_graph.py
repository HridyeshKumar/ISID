from pyvis.network import Network
from network_builder import G


# ---------------- CREATE NETWORK ----------------

net = Network(

    height="900px",

    width="100%",

    bgcolor="#111827",

    font_color="white",

    notebook=False
)


# ---------------- PHYSICS ----------------

net.barnes_hut()


# ---------------- ADD NODES ----------------

for node, data in G.nodes(data=True):

    color = "#94a3b8"
    size = 12

    # ---------- PROJECT ----------

    if node.startswith("PROJECT::"):

        color = "#60a5fa"
        size = 18

    # ---------- ACTOR ----------

    elif node.startswith("ACTOR::"):

        color = "#f59e0b"
        size = 22

    # ---------- LOCATION ----------

    elif node.startswith("LOCATION::"):

        color = "#22c55e"
        size = 16

    # ---------- TOPIC ----------

    elif node.startswith("TOPIC::"):

        color = "#ec4899"
        size = 18

    net.add_node(

        node,

        label=node.replace("::", "\n"),

        color=color,

        size=size,

        title=node
    )


# ---------------- ADD EDGES ----------------

for source, target in G.edges():

    net.add_edge(

        source,

        target
    )


# ---------------- OPTIONS ----------------

net.set_options("""

var options = {

  "nodes": {

    "font": {

      "size": 14

    }

  },

  "edges": {

    "color": {

      "inherit": true

    },

    "smooth": false

  },

  "physics": {

    "barnesHut": {

      "gravitationalConstant": -3000,

      "springLength": 140

    },

    "minVelocity": 0.75

  }

}

""")


# ---------------- SAVE ----------------

net.write_html(

    "templates/interactive_graph.html"
)

print(

    "\n🚀 Interactive graph created"

)

print(

    "📄 templates/interactive_graph.html"

)