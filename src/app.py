import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Groupe Projets App",
    page_icon="📊",
    layout="wide"
)

# Main header
st.title("📊 Groupe Projets Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")

# Main content area
st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
<h3 style='margin-top: 0;'>Welcome to the Project Dashboard</h3>
<p>Use the sidebar to navigate between different sections.</p>
</div>
""", unsafe_allow_html=True)

# Display information
st.info("This Streamlit app provides an interactive interface for managing and visualizing project data.")

# Example data display
st.subheader("Sample Data View")

# Create sample data
data = {
    'Project': ['Alpha', 'Beta', 'Gamma', 'Delta'],
    'Status': ['In Progress', 'Completed', 'Planning', 'In Review'],
    'Progress (%)': [75, 100, 20, 50]
}

df = pd.DataFrame(data)

# Display dataframe with styling
styled_df = df.style.format(
    {'Progress (%)': 'd.%'}
).apply(
    lambda s: s.map(
        lambda x: f'<span style="color: {get_progress_color(x)}">{x}</span>' if isinstance(x, (int, float)) else x,
        na_action='ignore'
    ),
    axis=1
)

st.dataframe(styled_df, use_container_width=True)

def get_progress_color(progress):
    """Get color based on progress percentage."""
    if progress >= 90:
        return "#28a745"
    elif progress >= 50:
        return "#ffc107"
    else:
        return "#dc3545"

# Footer
st.markdown("---")
st.caption("Groupe Projets App - Built with Streamlit")
