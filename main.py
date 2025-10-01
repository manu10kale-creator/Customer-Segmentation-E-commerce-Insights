import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

st.set_page_config(page_title="Customer Segmentation (Lite)", layout="wide")

st.title("🛍️ Customer Segmentation")
st.markdown("Customer segmentation using RFM features and KMeans clustering.")


@st.cache_data
def load_data():
    sheet_id = "1VaSPNh4rupxENsonEa3zDXq2Ojg1fMFg"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(csv_url)
    return df

df = load_data()
st.subheader("Data Preview")
st.dataframe(df.head())

id_col = "Customer ID"
date_col = "InvoiceDate"
qty_col = "Quantity"
price_col = "Price"


df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df["TotalPrice"] = df[qty_col] * df[price_col]

snapshot_date = df[date_col].max() + pd.Timedelta(days=1)
rfm = df.groupby(id_col).agg({
    date_col: lambda x: (snapshot_date - x.max()).days,
    id_col: "count",
    "TotalPrice": "sum"
}).rename(columns={date_col: "Recency", id_col: "Frequency", "TotalPrice": "Monetary"})

st.subheader("RFM Table")
st.dataframe(rfm.head())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(rfm)

n_clusters = 4  
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_scaled)
rfm["Cluster"] = labels

pca = PCA(2)
pcs = pca.fit_transform(X_scaled)
rfm["PC1"], rfm["PC2"] = pcs[:,0], pcs[:,1]

st.subheader("Cluster Visualization (PCA 2D)")
fig, ax = plt.subplots()
for c in np.unique(labels):
    subset = rfm[rfm["Cluster"] == c]
    ax.scatter(subset["PC1"], subset["PC2"], label=f"Cluster {c}", alpha=0.6)
ax.legend()
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
st.pyplot(fig)

st.subheader("Cluster Profiles (mean RFM)")
profile = rfm.groupby("Cluster")[["Recency","Frequency","Monetary"]].mean().round(2)
st.dataframe(profile)

st.subheader("Business Recommendations")
st.markdown("""
- **Low Recency, High Frequency & High Monetary = Champions** → Reward with loyalty perks.
- **High Recency, Low Frequency = At Risk** → Win-back campaigns, discounts.
- **High Frequency, Medium Monetary = Loyal** → Cross-sell / Upsell.
- **Low Frequency, Low Monetary = New / Casual** → Engagement emails, first-purchase offers.
""")
