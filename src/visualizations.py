"""
visualizations.py - Komponen grafik Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_match_distribution(df: pd.DataFrame):
    """Histogram distribusi tingkat pencocokan"""
    if df.empty or 'final_match_rate' not in df.columns:
        return go.Figure()
    
    df_unique = df.drop_duplicates(subset=['employee_id'])
    
    fig = px.histogram(
        df_unique,
        x='final_match_rate',
        title='Match Rate Distribution',
        labels={'final_match_rate': 'Final Match Rate (%)'},
        nbins=20
    )
    return fig

def plot_top_candidates(df: pd.DataFrame, top_n=10):
    """Grafik batang kandidat teratas"""
    if df.empty or 'final_match_rate' not in df.columns:
        return go.Figure()
    
    df_ranked = df.drop_duplicates(subset=['employee_id']).sort_values('final_match_rate', ascending=False)
    
    fig = px.bar(
        df_ranked.head(top_n),
        x='final_match_rate',
        y='fullname',
        orientation='h',
        title=f'Top {top_n} Candidates',
        labels={'final_match_rate': 'Match Rate (%)', 'fullname': 'Name'},
        text='final_match_rate'
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig

def plot_profile_comparison(df: pd.DataFrame, candidate_id: str, benchmark_ids: list):
    """Grafik radar perbandingan kandidat vs benchmark"""
    if df.empty or 'tgv_match_rate' not in df.columns:
        return go.Figure()
    
    candidate_data = df[df['employee_id'] == candidate_id].drop_duplicates(subset=['tgv_name'])
    benchmark_avg = df[df['employee_id'].isin(benchmark_ids)].groupby('tgv_name')['tgv_match_rate'].mean().reset_index()
    
    if candidate_data.empty:
        return go.Figure()
    
    comparison_df = pd.merge(
        candidate_data[['tgv_name', 'tgv_match_rate']],
        benchmark_avg,
        on='tgv_name',
        how='left',
        suffixes=('_candidate', '_benchmark')
    )
    
    # Hitung nilai maksimum untuk rentang dinamis
    max_value = comparison_df[['tgv_match_rate_candidate', 'tgv_match_rate_benchmark']].max().max()
    radial_range = [0, max(100, max_value * 1.1)]  # Minimal 100, perluas 10% di atas maksimum
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=comparison_df['tgv_match_rate_candidate'],
        theta=comparison_df['tgv_name'],
        fill='toself',
        name=f'Candidate ({candidate_id})'
    ))
    
    if not benchmark_avg.empty:
        fig.add_trace(go.Scatterpolar(
            r=comparison_df['tgv_match_rate_benchmark'],
            theta=comparison_df['tgv_name'],
            fill='toself',
            name='Benchmark Average'
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=radial_range)),
        title=f'TGV Profile Comparison: {candidate_data["fullname"].iloc[0]}',
        showlegend=True
    )
    return fig