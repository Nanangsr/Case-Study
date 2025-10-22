"""
visualizations.py - Komponen grafik Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st 

def plot_match_distribution(df: pd.DataFrame):
    """Histogram distribusi tingkat pencocokan"""
    
    if df.empty or 'final_match_rate' not in df.columns:
        st.warning("Data untuk 'Match Rate Distribution' kosong atau kolom hilang.")
        return go.Figure()
    
    df_unique = df.drop_duplicates(subset=['employee_id']).copy()
    
    # Jaga-jaga: Pastikan kolom numerik
    df_unique['final_match_rate'] = pd.to_numeric(df_unique['final_match_rate'], errors='coerce').fillna(0)
    df_unique['final_match_rate'] = df_unique['final_match_rate'].replace([np.inf, -np.inf], 0)
    
    if df_unique.empty:
        st.warning("Tidak ada data unik untuk 'Match Rate Distribution'.")
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df_unique['final_match_rate'].tolist(), # Gunakan .tolist()
        nbinsx=20,
        name='Distribusi'
    ))
    fig.update_layout(
        title='Match Rate Distribution',
        xaxis_title='Final Match Rate (%)',
        yaxis_title='Count (Jumlah Karyawan)'
    )
    
    return fig

def plot_top_candidates(df: pd.DataFrame, top_n=10):
    """Grafik batang kandidat teratas"""
    if df.empty or 'final_match_rate' not in df.columns or 'fullname' not in df.columns:
        st.warning("Data untuk 'Top Candidates' kosong atau kolom hilang.")
        return go.Figure()
    
    df_ranked = df.drop_duplicates(subset=['employee_id']).copy()
    
    # Jaga-jaga: Pastikan kolom numerik
    df_ranked['final_match_rate'] = pd.to_numeric(df_ranked['final_match_rate'], errors='coerce').fillna(0)
    df_ranked['final_match_rate'] = df_ranked['final_match_rate'].replace([np.inf, -np.inf], 0)
    
    df_ranked = df_ranked.sort_values('final_match_rate', ascending=False)
    
    if df_ranked.empty:
        st.warning("Tidak ada data unik untuk 'Top Candidates'.")
        return go.Figure()

    # Untuk go.Bar horizontal, data harus diurutkan ascending agar bar teratas ada di puncak
    plot_data = df_ranked.head(top_n).sort_values('final_match_rate', ascending=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_data['final_match_rate'].tolist(), # Gunakan .tolist()
        y=plot_data['fullname'].tolist(),        # Gunakan .tolist()
        orientation='h',
        text=plot_data['final_match_rate'].apply(lambda x: f'{x:.2f}%'), # Format teks
        textposition='outside', # Posisikan teks di luar bar
    ))
    
    fig.update_layout(
        title=f'Top {top_n} Candidates',
        xaxis_title='Match Rate (%)',
        yaxis_title='Name',
        yaxis=dict(tickfont=dict(size=10)) # Kecilkan font y-axis jika perlu
    )
    
    return fig

def plot_profile_comparison(df: pd.DataFrame, candidate_id: str, benchmark_ids: list):
    """Grafik radar perbandingan kandidat vs benchmark"""
    if df.empty or 'tgv_match_rate' not in df.columns:
        st.warning(f"Data TGV untuk perbandingan tidak ada (Kandidat: {candidate_id}).")
        return go.Figure()
    
    candidate_data = df[df['employee_id'] == candidate_id].drop_duplicates(subset=['tgv_name']).copy()
    benchmark_avg = df[df['employee_id'].isin(benchmark_ids)].groupby('tgv_name')['tgv_match_rate'].mean().reset_index()
    
    if candidate_data.empty:
        st.warning(f"Tidak ada data TGV untuk kandidat {candidate_id}.")
        return go.Figure()
    
    # Jaga-jaga: Pastikan kolom numerik
    candidate_data['tgv_match_rate'] = pd.to_numeric(candidate_data['tgv_match_rate'], errors='coerce').fillna(0)
    candidate_data['tgv_match_rate'] = candidate_data['tgv_match_rate'].replace([np.inf, -np.inf], 0)
    
    benchmark_avg['tgv_match_rate'] = pd.to_numeric(benchmark_avg['tgv_match_rate'], errors='coerce').fillna(0)
    benchmark_avg['tgv_match_rate'] = benchmark_avg['tgv_match_rate'].replace([np.inf, -np.inf], 0)
    
    comparison_df = pd.merge(
        candidate_data[['tgv_name', 'tgv_match_rate', 'fullname']], # Ambil fullname
        benchmark_avg,
        on='tgv_name',
        how='left',
        suffixes=('_candidate', '_benchmark')
    )
    
    # Jaga-jaga: Isi NaN dari merge
    comparison_df['tgv_match_rate_candidate'] = comparison_df['tgv_match_rate_candidate'].fillna(0)
    comparison_df['tgv_match_rate_benchmark'] = comparison_df['tgv_match_rate_benchmark'].fillna(0)
    
    # Hitung nilai maksimum untuk rentang dinamis
    max_val_candidate = comparison_df['tgv_match_rate_candidate'].max()
    max_val_benchmark = comparison_df['tgv_match_rate_benchmark'].max()
    max_value = max(max_val_candidate, max_val_benchmark)
    radial_range = [0, max(100, max_value * 1.1)] # Minimal 100, perluas 10% di atas maksimum
    
    candidate_name = comparison_df["fullname"].iloc[0] # Ambil nama
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=comparison_df['tgv_match_rate_candidate'].tolist(),
        theta=comparison_df['tgv_name'].tolist(),
        fill='toself',
        name=f'Candidate ({candidate_name})' # Gunakan nama
    ))
    
    if not benchmark_avg.empty:
        fig.add_trace(go.Scatterpolar(
            r=comparison_df['tgv_match_rate_benchmark'].tolist(),
            theta=comparison_df['tgv_name'].tolist(),
            fill='toself',
            name='Benchmark Average'
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=radial_range)),
        title=f'TGV Profile Comparison: {candidate_name}', # Gunakan nama
        showlegend=True
    )
    return fig
