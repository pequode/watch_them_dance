from hr_game.creation.employee import randomize_employee
from hr_game.creation.network import create_fully_connected_network
from hr_game.data.employee import Employee, EmployeeNetwork
import numpy as np 
from matplotlib import pyplot as plt 
import community.community_louvain as community_louvain
import networkx as nx 

def show_traits(employees:list[Employee])->tuple[plt.Figure,plt.Axes]:
    # Traits to plot (skip context_history/traits lists)
    numeric_traits = ["stress", "greed", "salary", "anger", "horniness",
                      "happiness", "productivity", "health"]

    names = [e.name for e in employees]

    # Collect trait values for each employee
    data = {trait: [getattr(e, trait) for e in employees] for trait in numeric_traits}

    # Normalize salary to 0-100 scale
    salaries = data["salary"]
    if max(salaries) > 0:  # avoid divide by zero
        max_salary = max(salaries)
        data["salary"] = [int((s / max_salary) * 100) for s in salaries]

    # Set up plotting
    x = np.arange(len(employees))  # positions for employees
    width = 0.1                     # width of each bar
    offset = np.linspace(-width*len(numeric_traits)/2, 
                         width*len(numeric_traits)/2, 
                         len(numeric_traits))

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot each trait as a different bar
    for i, trait in enumerate(numeric_traits):
        ax.bar(x + offset[i], data[trait], width, label=trait)

    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Value (0–100, salary normalized)")
    ax.set_title("Employee Traits Comparison")
    ax.set_ylim(0, 100)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")  # put legend outside

    fig.tight_layout()
    return fig, ax
    

def show_romance(network:EmployeeNetwork):
    """
    Plot a graph where edges have fixed width, but color ranges from grey to red
    based on attraction (0=grey, 1=red).
    """
    employees = network.employees
    relationships = network.relationships
    G = nx.Graph()

    # Add nodes
    for e in employees.values():
        G.add_node(e.name)

    # Add edges with friendship as weight
    for e1_id, e2_id, rel in relationships:
        e1 = employees[e1_id]
        e2 = employees[e2_id]
        G.add_edge(e1.name, e2.name, attraction=rel.attraction)

    # Force-directed layout
    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=500, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)

    # Draw edges with fixed width, color based on attraction
    edges = G.edges(data=True)
    edge_colors = []
    for _, _, d in edges:
        # Map 0 → grey (#888888), 1 → red (#FF0000)
        r = int(255 * d["attraction"])
        g = int(0)
        b = int(0)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        edge_colors.append(hex_color)

    nx.draw_networkx_edges(G, pos, width=2, edge_color=edge_colors, ax=ax)

    ax.set_title("Employee Attraction Graph")
    ax.axis("off")
    fig.tight_layout()
    return fig, ax

def graph_closeness(network:EmployeeNetwork):
    """
    Plot friendship graph with community detection coloring.
    """
    employees = network.employees
    relationships = network.relationships
    G = nx.Graph()

    # Add nodes
    for e in employees.values():
        G.add_node(e.name)

    # Add edges with friendship as weight
    for e1_id, e2_id, rel in relationships:
        e1 = employees[e1_id]
        e2 = employees[e2_id]
        G.add_edge(e1.name, e2.name, weight=rel.friendship)

    pos = nx.spring_layout(G, weight="weight", seed=42)

    # Louvain community detection
    partition = community_louvain.best_partition(G, weight="weight")

    # Colors by community
    node_colors = [partition[n] for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(8, 6))

    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           cmap=plt.cm.Set3, node_size=600, ax=ax)
    weights = [d["weight"] * 5 for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.6, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)

    ax.set_title("Employee Friendship Communities")
    ax.axis("off")
    fig.tight_layout()
    return fig, ax
employees =[randomize_employee() for i in range(10)]
network = create_fully_connected_network(employees=employees)
# # traits 
fig,ax = show_traits(employees)
fig.savefig(".plots/employee_traits.png", dpi=300)
# closeness 
fig1,ax1 = graph_closeness(network)
fig1.savefig(".plots/employee_graph1.png", dpi=300)
# romances 
fig2,ax2 = show_romance(network)
fig2.savefig(".plots/employee_graph2.png", dpi=300)