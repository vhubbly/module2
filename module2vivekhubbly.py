import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

BASE_URL = 'https://en.wikipedia.org'
START_PAGE = '/wiki/Data_science'

def get_wikipedia_links(page, max_links=20):
    """Scrapes Wikipedia page for internal links."""
    url = BASE_URL + page
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = set()
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('/wiki/') and ':' not in href and len(links) < max_links:
            links.add(href)
    return list(links)

num_pages = 5  # Number of Wikipedia pages to explore
graph_data = {}

queue = [START_PAGE]
visited = set()

while queue and len(visited) < num_pages:
    page = queue.pop(0)
    if page in visited:
        continue
    visited.add(page)

    links = get_wikipedia_links(page)
    graph_data[page] = links

    for link in links:
        if link not in visited and link not in queue:
            queue.append(link)

# Convert to edge list
edges = [(source, target) for source, targets in graph_data.items() for target in targets]

# Create a directed graph
G = nx.DiGraph()
G.add_edges_from(edges)

# Compute PageRank scores
pagerank = nx.pagerank(G)

# Find the top 3 most important nodes
top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:3]

# Print results with direct hyperlinks
print("\nTop 3 important Wikipedia articles based on PageRank:")
for node, score in top_nodes:
    clean_node = node.replace("/wiki/", "").replace("_", " ")
    url = BASE_URL + node
    print(f"{clean_node}: {score:.5f} ({url})")

# Draw the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G)

# Draw all nodes
nx.draw(G, pos, with_labels=False, node_size=50, font_size=10, edge_color="gray", alpha=0.7)

# Highlight and label the top 3 important nodes in red
top_nodes_set = {node for node, _ in top_nodes}
node_colors = ['red' if node in top_nodes_set else 'lightblue' for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=100)
nx.draw_networkx_labels(G, pos, labels={node: node.replace("/wiki/", "").replace("_", " ") for node in top_nodes_set}, font_size=8, font_color="red")

plt.title("Wikipedia Article Link Network")
plt.show()
