from pathlib import Path
import os

import pandas as pd
import networkx as nx

# The cit-Patents dataset is a citation graph for US patents.
# https://snap.stanford.edu/data/cit-Patents.html

# The purpose of the script is to find the nodes (US patents) that are highly
# "central" to other nodes, meaning they are cited by multiple patents and
# therefore represent "connections" between patents.  Patents that connect
# other patents this way could be thought of as "more important" than others.
#
# This script reads the dataset CSV representing the citation graph edgelist
# into a Pandas DataFrame, which is then used to create a NetworkX directed
# Graph.  The NetworkX Graph object is used for the betweenness_centrality
# call, which returns a dictionary mapping node IDs to betweenness centrality
# scores (the higher the score, the more central the node)
#
# Betweenness centrality is an approximation algorithm that picks k
# randomly-chosen shortest paths for each node.  The algorithm checks if each
# node is present in the k shortest paths, and if so, it updates the node's
# betweenness centrality score appropriately.  A node that is more central will
# show up in more shortest paths and have a higher score.
#
# The value of k is significant since a higher value will provide more paths to
# check and therefore a more accurate score for each node.
#
# The betweenness centrality scores are used to create another Pandas DataFrame
# to group the nodes into two bins - a lower scoring bin and a higher scoring
# bin.  A user can modify the thresholds for the bins to help find the more
# central nodes.

k = 100
# See download_datsets.sh for downloading the CSV file.
edgelist_csv = Path(
    os.environ.get("RAPIDS_DATASET_ROOT_DIR",
                   Path(__file__).parent)
) / "cit-Patents.csv"
edgelist_df = pd.read_csv(edgelist_csv, sep=" ", names=["source", "target"])

G = nx.from_pandas_edgelist(edgelist_df, create_using=nx.DiGraph)
bc_values_dict = nx.betweenness_centrality(G, k=k)

bc_values_df = pd.DataFrame(bc_values_dict.items(), columns=["node", "bc"])

max_bc = bc_values_df["bc"].max()
bins = [0, max_bc * .5, max_bc]
bc_bins = pd.cut(bc_values_df["bc"], bins, include_lowest=True)
groups = bc_values_df.groupby(bc_bins)

print(f"{k=}")
#print(groups.size())  # "unhashable type: dict" error when using cudf.pandas
print(groups.count()["node"])
