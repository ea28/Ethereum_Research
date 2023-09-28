import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def get_last_name(full_name):
    """Extract the last name from a full name."""
    parts = full_name.split()
    return parts[-1] if parts else full_name

# Load the CSV file
data = pd.read_csv('AllEIPs.csv')

# Extract last names and build the co-authorship graph using these last names
data['LastName'] = data['Author'].apply(get_last_name)

# Create an empty graph for last names
G_last_name = nx.Graph()

# Iterate through each row in the dataset to construct the co-authorship graph using last names
for _, row in data.iterrows():
    authors = [get_last_name(author.strip()) for author in row['Author'].split(',')]
    for author in authors:
        if author not in G_last_name:
            G_last_name.add_node(author)
    for i in range(len(authors)):
        for j in range(i+1, len(authors)):
            if G_last_name.has_edge(authors[i], authors[j]):
                G_last_name[authors[i]][authors[j]]['weight'] += 1
            else:
                G_last_name.add_edge(authors[i], authors[j], weight=1)

# Remove self-loops from the graph
G_last_name.remove_edges_from(nx.selfloop_edges(G_last_name))


# Remove nodes with no edges (i.e., no co-authors)
isolates = list(nx.isolates(G_last_name))
G_last_name.remove_nodes_from(isolates)

# Compute betweenness centrality for each author's last name in the graph
betweenness_centrality_last_name = nx.betweenness_centrality(G_last_name, weight='weight')

# Adjust the graph drawing function for better visualization
def plot_bc_graph(G, betweenness_centrality):
    plt.figure(figsize=(20, 20))
    node_size = [v * 20000 for v in betweenness_centrality.values()]
    pos = nx.spring_layout(G, k=0.5, iterations=100)
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', edgecolors='black')
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    plt.title('Betweenness Centrality of Ethereum EIP Co-authorship Graph', fontsize=25, fontweight='bold')
    plt.axis('off')
    plt.savefig('EIPBetweennessCentrality.png')
    plt.show()

# Draw the graph
plot_bc_graph(G_last_name, betweenness_centrality_last_name)

# Count the number of EIPs each author has co-authored
author_eip_count = {}
for _, row in data.iterrows():
    authors = [get_last_name(author.strip()) for author in row['Author'].split(',')]
    for author in authors:
        author_eip_count[author] = author_eip_count.get(author, 0) + 1

# Extract the top 20 authors with the highest betweenness centrality and include EIP count
top_20_authors_info = [(author, centrality, author_eip_count[author])
                       for author, centrality in sorted(betweenness_centrality_last_name.items(), key=lambda x: x[1], reverse=True)[:20]]
print(top_20_authors_info)
