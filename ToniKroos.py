
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Sbopen

# Set page config
st.set_page_config(
    page_title="StatsBomb Football Analytics",
    page_icon="⚽",
    layout="wide"
)

# Title
st.title("⚽ StatsBomb Football Analytics Dashboard")

# Initialize parser
parser = Sbopen()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Competition Data", 
    "📊 Match Data", 
    "🎯 Player Pass Map",
    "📈 Player Comparison"
])

# Tab 1: Competition Data
with tab1:
    st.header("Competition Data")
    
    try:
        df_competition = parser.competition()
        
        # Display basic info
        st.write(f"**Total Competitions:** {len(df_competition)}")
        st.write(f"**Columns in data:** {', '.join(df_competition.columns.tolist())}")
        
        # Show data table
        st.dataframe(df_competition, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading competition data: {e}")

# Tab 2: Match Data
with tab2:
    st.header("Match Data")
    
    try:
        df_match = parser.match(competition_id=55, season_id=282)
        
        # Display basic info
        st.write(f"**Total Matches:** {len(df_match)}")
        st.write(f"**Columns in data:** {', '.join(df_match.columns.tolist())}")
        
        # Show data table
        st.dataframe(df_match, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading match data: {e}")

# Tab 3: Player Pass Map
with tab3:
    st.header("Player Pass Map")
    
    try:
        # Load event data
        df_event, df_related, df_freeze, df_tactics = parser.event(3930158)
        
        # Show event data info
        st.write(f"**Total Events:** {len(df_event)}")
        st.write(f"**Columns in event data:** {', '.join(df_event.columns.tolist())}")
        
        # Filter for Kroos' passes
        kroos_passes = df_event[(df_event['player_name'] == 'Toni Kroos') & (df_event['type_name'] == 'Pass')]
        
        st.write(f"**Toni Kroos Passes:** {len(kroos_passes)}")
        
        # Create pass map visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Starting position of each pass
        ax.scatter(kroos_passes['x'], kroos_passes['y'], 
                  c='blue', alpha=0.6, s=30, zorder=3)
        
        # Pass arrows
        for _, row in kroos_passes.iterrows():
            ax.arrow(row['x'], row['y'], 
                    row['end_x'] - row['x'], 
                    row['end_y'] - row['y'],
                    head_width=1.2, head_length=1.5, 
                    fc='blue', ec='blue', alpha=0.45, length_includes_head=True, zorder=2)
        
        # Pitch markings
        ax.hlines([0, 20, 40, 60, 80, 100], 0, 120, color='gray', alpha=0.3, linewidth=0.8)
        ax.vlines([0, 40, 80, 120], 0, 100, color='gray', alpha=0.3, linewidth=0.8)
        
        ax.set_title("Toni Kroos Pass Map vs Scotland (Euro 2024)", 
                    fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel("Pitch Width (0-120)", fontsize=12)
        ax.set_ylabel("Pitch Length (0-100)", fontsize=12)
        
        # Add a subtle background gradient to show attacking direction
        ax.axhspan(60, 100, alpha=0.05, color='green', label="Scotland's half")
        
        ax.grid(True, alpha=0.2)
        ax.legend()
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig)
        
        # Show pass data
        st.subheader("Pass Data")
        st.dataframe(kroos_passes[['minute', 'second', 'location', 'end_location', 'pass_outcome_name']].head(20))
        
    except Exception as e:
        st.error(f"Error loading event data: {e}")

# Tab 4: Player Comparison
with tab4:
    st.header("Player Comparison")
    
    # Create simple dataset for 5 key midfielders
    data = {
        'Player': ['Toni Kroos', 'Rodri', 'Jude Bellingham', 'Kevin De Bruyne', 'Nicolò Barella'],
        'Team': ['Germany', 'Spain', 'England', 'Belgium', 'Italy'],
        'Matches': [5, 5, 5, 3, 4],
        
        # Key metrics (per 90 minutes)
        'Pass_Accuracy': [94.2, 93.8, 88.3, 90.8, 88.9],
        'Passes_90': [89.4, 95.2, 62.3, 84.3, 68.5],
        'Progressive_Passes_90': [8.2, 7.9, 5.4, 8.1, 6.5],
        'Key_Passes_90': [2.8, 1.9, 3.1, 3.3, 2.1],
        'Assists': [3, 2, 2, 2, 1],
        'Ball_Recoveries_90': [6.8, 8.2, 7.1, 6.9, 7.4],
        'Touches_90': [98.5, 102.3, 72.8, 94.7, 82.1],
    }
    
    df = pd.DataFrame(data)
    
    # Display the dataframe
    st.dataframe(df, use_container_width=True)
    
    # Calculate Z-scores
    metrics = ['Pass_Accuracy', 'Passes_90', 'Progressive_Passes_90', 'Key_Passes_90', 'Ball_Recoveries_90']
    
    z_scores = pd.DataFrame()
    z_scores['Player'] = df['Player']
    
    for metric in metrics:
        mean = df[metric].mean()
        std = df[metric].std()
        z_scores[metric] = (df[metric] - mean) / std
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Bar chart of Z-scores
    x = np.arange(len(metrics))
    width = 0.15
    colors = ['black', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for idx, player in enumerate(df['Player']):
        player_z = z_scores[z_scores['Player'] == player].iloc[0]
        scores = [player_z[m] for m in metrics]
        ax1.bar(x + idx*width - 2*width, scores, width, label=player, color=colors[idx], alpha=0.8)
    
    ax1.set_ylabel('Z-Score')
    ax1.set_title('Z-Score Comparison: 5 Elite Midfielders')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.replace('_', '\n') for m in metrics])
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Kroos' profile
    ax2.barh(range(len(metrics)), z_scores[z_scores['Player'] == 'Toni Kroos'].iloc[0][metrics].values)
    ax2.set_yticks(range(len(metrics)))
    ax2.set_yticklabels([m.replace('_', ' ') for m in metrics])
    ax2.set_xlabel('Z-Score')
    ax2.set_title('Toni Kroos: Standard Deviations from Mean')
    ax2.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, score in enumerate(z_scores[z_scores['Player'] == 'Toni Kroos'].iloc[0][metrics].values):
        color = 'green' if score > 0 else 'red'
        ax2.text(score + (0.1 if score >= 0 else -0.3), i, f'{score:.2f}', 
                va='center', fontweight='bold', color=color)
    
    plt.tight_layout()
    
    # Display the plot
    st.pyplot(fig)
    
    # Print summary
    st.subheader("Z-Score Summary")
    
    for player in df['Player']:
        with st.expander(f"{player}"):
            player_z = z_scores[z_scores['Player'] == player].iloc[0]
            for metric in metrics:
                z = player_z[metric]
                interpretation = "++" if z > 1.5 else "+" if z > 0.5 else "≈" if abs(z) <= 0.5 else "-" if z < -0.5 else "--"
                st.write(f"{metric}: Z = {z:.2f} | {interpretation}")

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.write("""
    This dashboard uses StatsBomb data to analyze football matches.
    
    Features:
    - Competition data overview
    - Match data exploration
    - Player pass map visualization
    - Player performance comparison
    """)
    
    st.header("Data Source")
    st.write("StatsBomb Open Data")
    
    st.header("Match ID")
    st.write("Current analysis uses match ID: 3930158")
    
    st.header("Player")
    st.write("Focus player: Toni Kroos")