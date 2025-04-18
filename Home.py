import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_autorefresh import st_autorefresh

# --- Page Config ---
st.set_page_config(page_title="Multi-Lane Vehicle Monitoring", layout="wide")

# --- Background + Section Styling ---
st.markdown(
    """
    <style>
    body {
        background-color: #FFF0F5;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .section {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Refresh Toggle ---
refresh_toggle = st.sidebar.checkbox("🔄 Auto Refresh Every 10 Seconds", value=True)
if refresh_toggle:
    st_autorefresh(interval=10 * 1000, key="auto_refresh")

# --- MySQL Connection ---
def connect_db():
    return mysql.connector.connect(
        host="host name",
        user="user name",
        password="your password",
        database="multi_vehicle_data"
    )

# --- Fetch Data ---
def fetch_data():
    conn = connect_db()
    query = "SELECT * FROM lane_vehicle_count"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Load Data ---
df = fetch_data()
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['formatted_time'] = df['timestamp'].dt.strftime('%H:%M:%S')

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.title("🚦 Multi-Lane Vehicle Count Dashboard")
st.markdown("</div>", unsafe_allow_html=True)

# --- Raw Data ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
with st.expander("📄 View Raw Data"):
    st.dataframe(df)
st.markdown("</div>", unsafe_allow_html=True)

# --- Summary ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🔢 Total Vehicle Count Summary")
total_data = {
    "Lane 1 Forward": df['lane1_fwd'].sum(),
    "Lane 1 Backward": df['lane1_bwd'].sum(),
    "Lane 2 Forward": df['lane2_fwd'].sum(),
    "Lane 2 Backward": df['lane2_bwd'].sum(),
    "Lane 3 Forward": df['lane3_fwd'].sum(),
    "Lane 3 Backward": df['lane3_bwd'].sum(),
    "Lane 4 Forward": df['lane4_fwd'].sum(),
    "Lane 4 Backward": df['lane4_bwd'].sum(),
}
summary_df = pd.DataFrame(list(total_data.items()), columns=["Direction", "Total Count"])
st.bar_chart(summary_df.set_index("Direction"))
st.markdown("</div>", unsafe_allow_html=True)

# --- Traffic Flow Charts ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📈 Traffic Flow Over Time")
lanes = {
    "Lane 1 Forward": "lane1_fwd",
    "Lane 1 Backward": "lane1_bwd",
    "Lane 2 Forward": "lane2_fwd",
    "Lane 2 Backward": "lane2_bwd",
    "Lane 3 Forward": "lane3_fwd",
    "Lane 3 Backward": "lane3_bwd",
    "Lane 4 Forward": "lane4_fwd",
    "Lane 4 Backward": "lane4_bwd",
}
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
cols = st.columns(4)
for idx, (lane_name, col_name) in enumerate(lanes.items()):
    with cols[idx % 4]:
        fig, ax = plt.subplots(figsize=(6, 3))
        sns.lineplot(x=df['formatted_time'], y=df[col_name], marker='o', ax=ax, color=colors[idx])
        ax.set_title(f"{lane_name}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Vehicle Count")
        plt.xticks(rotation=45)
        fig.tight_layout()
        st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# --- Traffic Light Suggestion ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🚥 Suggested Traffic Light Status")
lane_totals = {
    "Lane 1": df['lane1_fwd'].iloc[-1] + df['lane1_bwd'].iloc[-1],
    "Lane 2": df['lane2_fwd'].iloc[-1] + df['lane2_bwd'].iloc[-1],
    "Lane 3": df['lane3_fwd'].iloc[-1] + df['lane3_bwd'].iloc[-1],
    "Lane 4": df['lane4_fwd'].iloc[-1] + df['lane4_bwd'].iloc[-1],
}
sorted_lanes = sorted(lane_totals.items(), key=lambda x: x[1], reverse=True)
default_light_status = {}
for i, (lane, count) in enumerate(sorted_lanes):
    if i == 0:
        default_light_status[lane] = "🟢 GREEN"
    elif i in [1, 2]:
        default_light_status[lane] = "🟡 YELLOW"
    else:
        default_light_status[lane] = "🔴 RED"
st.markdown("</div>", unsafe_allow_html=True)

# --- Manual Override Buttons ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🎛️ Manual Override")
override_cols = st.columns(4)
final_light_status = {}
for i, lane in enumerate(["Lane 1", "Lane 2", "Lane 3", "Lane 4"]):
    with override_cols[i]:
        st.markdown(f"**{lane}**")
        if st.button(f"🔴 RED ({lane})"):
            final_light_status[lane] = "🔴 RED"
        elif st.button(f"🟡 YELLOW ({lane})"):
            final_light_status[lane] = "🟡 YELLOW"
        elif st.button(f"🟢 GREEN ({lane})"):
            final_light_status[lane] = "🟢 GREEN"
        else:
            final_light_status[lane] = default_light_status.get(lane, "🔴 RED")

status_cols = st.columns(4)
for i, lane in enumerate(["Lane 1", "Lane 2", "Lane 3", "Lane 4"]):
    with status_cols[i]:
        st.metric(label=f"{lane} Status", value=final_light_status[lane])
st.markdown("</div>", unsafe_allow_html=True)

# --- Max Count Lane ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🚗 Lane with Maximum Count in Last Interval")
max_lane = max(lane_totals, key=lane_totals.get)
st.info(f"Highest vehicle count in last interval: **{max_lane}** with **{lane_totals[max_lane]}** vehicles.")
st.markdown("</div>", unsafe_allow_html=True)

# --- Download Report ---
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📥 Download Vehicle Count Report")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download .CSV Report", data=csv, file_name='vehicle_count_report.csv', mime='text/csv')
st.markdown("</div>", unsafe_allow_html=True)
