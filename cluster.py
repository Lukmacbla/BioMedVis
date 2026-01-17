import pandas as pd
import numpy as np
import networkx as nx
from pyvis.network import Network
import streamlit as st
import tempfile



@st.cache_data
def build_graph(df, min_cooccurrence, readmission_type, med_cols):
    taken_medication = (df[med_cols] != "No").astype(int)
    # Readmission definition
    if readmission_type == "Any":
        readmit = df["readmitted"].isin([">30", "<30"]).astype(int)
    else:
        readmit = (df["readmitted"] == "<30").astype(int)

    med_freq = taken_medication.sum()
    med_readmit = {
        med: float(readmit[taken_medication[med] == 1].mean())
        for med in med_cols
    }

    co_matrix = (taken_medication.T @ taken_medication).to_numpy()

    G = nx.Graph()

    for med in med_cols:
        freq = int(med_freq[med])
        readmit_value = float(med_readmit[med])
        if freq > 0:
            G.add_node(
                med,
                freq=freq,
                readmit=readmit_value
            )

    for i, m1 in enumerate(med_cols):
        for j, m2 in enumerate(med_cols):
            if i < j and co_matrix[i, j] >= min_cooccurrence:
                value = float(co_matrix[i, j]) / float(min(freq, int(med_freq[m2])))
                G.add_edge(m1, m2, value=value)

    return G

def render_graph(G, size_mode):
    net = Network(height="750px", width="100%")

    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=150,
        spring_strength=0.08
    )

    net.from_nx(G)

    for node in net.nodes:
        freq = int(G.nodes[node["id"]]["freq"])
        readmit = float(G.nodes[node["id"]]["readmit"])

        if size_mode == "Medication frequency":
            node["size"] = float(10 + freq * 0.002)
        else:
            node["size"] = float(10 + readmit * 40)

        node["color"] = (
            f"rgba({int(255*readmit)}, {int(255*(1-readmit))}, 0, 0.85)"
        )

        node["title"] = (
            f"<b>{node['id']}</b><br>"
            f"Patients: {freq}<br>"
            f"Readmission rate: {readmit:.1%}"
        )

    for edge in net.edges:
        edge["value"] = float(edge.get("value", 1))
        edge["width"] = float(edge["value"]) * 5

    return net