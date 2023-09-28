import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations


def remove_names(author_list, names_to_remove):
    """Remove specific names from the author list and strip extra spaces."""
    return ', '.join([author.strip() for author in author_list if author.strip() not in names_to_remove])


def format_input_data(data, names_to_remove):
    """Format the input DataFrame and remove specific names from 'Author' column."""
    data.drop_duplicates(inplace=True)
    grouped_data = data.groupby('EIP_Number')['Author'].apply(', '.join).reset_index()
    grouped_data['Author'] = grouped_data['Author'].apply(lambda x: remove_names(x.split(','), names_to_remove))
    return grouped_data


def create_and_analyze_graph(data):
    """Create a graph from input DataFrame, calculate betweenness centrality, and return a subgraph and centrality."""
    G = nx.Graph()
    for index, row in data.iterrows():
        authors = str(row['Author']).split(', ')
        for combo in combinations(authors, 2):
            if G.has_edge(*combo):
                G[combo[0]][combo[1]]['weight'] += 1
            else:
                G.add_edge(*combo, weight=1)

    betweenness_centrality = nx.betweenness_centrality(G, weight='weight')
    non_zero_bc_nodes = [node for node, bc in betweenness_centrality.items() if bc > 0]
    G_subgraph = G.subgraph(non_zero_bc_nodes)

    return G_subgraph, betweenness_centrality


def plot_bc_graph(G, betweenness_centrality):
    """Plot graph with nodes represented by authors and edges representing co-authorships, highlighting betweenness centrality."""
    plt.figure(figsize=(20, 20))
    node_size = [v * 20000 for v in betweenness_centrality.values()]
    pos = nx.spring_layout(G, k=1, iterations=100)
    last_name_labels = {node: node.split()[-1] for node in G.nodes()}
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', edgecolors='black')
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, labels=last_name_labels, font_size=10, font_weight='bold')
    plt.title('Betweenness Centrality of Ethereum EIP Github Commits', fontsize=15,
              fontweight='bold')
    plt.axis('off')
    plt.savefig('CommitBetweennessCentrality.png')
    plt.show()


def main():
    # Define parameters
    input_file = "updated_commits.csv"
    names_to_remove = ['Pandapip1', 'eth-bot']

    # Load the CSV file into a DataFrame
    data = pd.read_csv(input_file)

    # Format the input data
    formatted_data = format_input_data(data, names_to_remove)

    # Create and analyze graph
    G_subgraph, betweenness_centrality = create_and_analyze_graph(formatted_data)

    # Plot the graph
    plot_bc_graph(G_subgraph, {k: v for k, v in betweenness_centrality.items() if k in G_subgraph.nodes()})

    # Save the betweenness centrality data to a CSV file
    bc_data = pd.DataFrame(list(betweenness_centrality.items()), columns=['Author', 'Betweenness_Centrality'])
    bc_data.to_csv("betweenness_centrality.csv", index=False)


if __name__ == "__main__":
    main()
