"""
database.py - Operasi basis data melalui REST API Supabase
"""
import pandas as pd
import numpy as np
import requests
import logging

from config import Config

# Pengaturan logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')

headers = {
    "apikey": Config.SUPABASE_KEY,
    "Authorization": f"Bearer {Config.SUPABASE_KEY}",
    "Prefer": "count=exact"
}

def load_table(table_name, batch_size=1000):
    """Muat semua data dari tabel Supabase dengan paginasi"""
    all_data = []
    offset = 0
    
    while True:
        url = f"{Config.SUPABASE_URL}/rest/v1/{table_name}"
        params = {"select": "*", "limit": batch_size, "offset": offset}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            batch = response.json()
            
            if not batch:
                break
                
            all_data.extend(batch)
            offset += len(batch)
            
            if len(batch) < batch_size:
                break
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error loading table {table_name}: {str(e)}")
            return pd.DataFrame()
    
    logging.info(f"Loaded table {table_name} with {len(all_data)} rows")
    return pd.DataFrame(all_data)

def get_employee_list():
    """Dapatkan daftar karyawan untuk dropdown"""
    df = load_table("employees")
    if df.empty:
        return pd.DataFrame({'employee_id': [], 'label': []})
    
    df['label'] = df['fullname'] + " (" + df['employee_id'] + ")"
    return df[['employee_id', 'label']].sort_values('label')

def get_role_list():
    """Dapatkan nama peran unik"""
    df = load_table("dim_positions")
    if df.empty or 'name' not in df.columns:
        return []
    return sorted(df['name'].dropna().unique().tolist())

def run_matching_query(benchmark_ids: list):
    """
    Algoritma pencocokan inti
    Mengembalikan: DataFrame dengan hasil pencocokan
    """
    logging.info(f"Starting matching for benchmarks: {benchmark_ids}")
    if not benchmark_ids:
        logging.warning("No benchmark IDs provided")
        return pd.DataFrame()
    
    # Muat tabel yang diperlukan
    df_psych = load_table("profiles_psych")
    df_comp = load_table("competencies_yearly")
    df_papi = load_table("papi_scores")
    df_mapping = load_table("dim_talent_mapping")
    
    if any(df.empty for df in [df_psych, df_comp, df_papi, df_mapping]):
        logging.error("One or more source tables empty")
        return pd.DataFrame()
    
    # Konversi kolom numerik
    for col in ['iq', 'pauli']:
        if col in df_psych.columns:
            df_psych[col] = pd.to_numeric(df_psych[col], errors='coerce')
    
    df_comp['score'] = pd.to_numeric(df_comp['score'], errors='coerce')
    df_comp['year'] = pd.to_numeric(df_comp['year'], errors='coerce')
    df_papi['score'] = pd.to_numeric(df_papi['score'], errors='coerce')
    
    # Dapatkan tahun kompetensi terbaru
    latest_year = df_comp['year'].max()
    df_comp_latest = df_comp[df_comp['year'] == latest_year].copy()
    df_comp_latest.rename(columns={'pillar_code': 'tv_name', 'score': 'tv_value'}, inplace=True)
    
    # Gabungkan semua skor
    scores_list = []
    
    if 'iq' in df_psych.columns:
        scores_list.append(
            df_psych[['employee_id', 'iq']].copy()
            .rename(columns={'iq': 'tv_value'})
            .assign(tv_name='iq')
        )
    
    if 'pauli' in df_psych.columns:
        scores_list.append(
            df_psych[['employee_id', 'pauli']].copy()
            .rename(columns={'pauli': 'tv_value'})
            .assign(tv_name='pauli')
        )
    
    scores_list.append(df_comp_latest[['employee_id', 'tv_name', 'tv_value']].copy())
    scores_list.append(
        df_papi[['employee_id', 'scale_code', 'score']].copy()
        .rename(columns={'scale_code': 'tv_name', 'score': 'tv_value'})
    )
    
    all_scores_df = pd.concat(scores_list, ignore_index=True).dropna(subset=['tv_value'])
    
    # Gabung dengan mapping
    scores_with_details = pd.merge(
        all_scores_df,
        df_mapping[['Sub-test', 'Talent Group Variable (TGV)', 'Meaning', 'Behavior Example', 'Note']],
        left_on='tv_name',
        right_on='Sub-test',
        how='inner'
    )
    scores_with_details.rename(columns={'Talent Group Variable (TGV)': 'tgv_name'}, inplace=True)
    
    # Hitung baseline benchmark (median)
    benchmark_data = scores_with_details[scores_with_details['employee_id'].isin(benchmark_ids)]
    benchmark_baseline = benchmark_data.groupby('tv_name')['tv_value'].median().reset_index()
    benchmark_baseline.rename(columns={'tv_value': 'baseline_score'}, inplace=True)
    
    # Hitung tingkat pencocokan TV
    tv_match_rates = pd.merge(scores_with_details, benchmark_baseline, on='tv_name', how='left')
    tv_match_rates.rename(columns={'tv_value': 'user_score'}, inplace=True)
    tv_match_rates['tv_match_rate'] = 0.0
    
    # Tangani skala inverse
    is_inverse = tv_match_rates['Note'].fillna('').str.contains('Inverse Scale', case=False, na=False)
    
    # Skala normal (semakin tinggi semakin baik)
    mask_normal = ~is_inverse & tv_match_rates['baseline_score'].notna() & (tv_match_rates['baseline_score'] != 0)
    tv_match_rates.loc[mask_normal, 'tv_match_rate'] = (
        tv_match_rates.loc[mask_normal, 'user_score'] / 
        tv_match_rates.loc[mask_normal, 'baseline_score']
    ) * 100.0
    
    # Skala inverse (semakin rendah semakin baik)
    mask_inverse = is_inverse & tv_match_rates['baseline_score'].notna() & (tv_match_rates['baseline_score'] != 0)
    user = tv_match_rates.loc[mask_inverse, 'user_score']
    base = tv_match_rates.loc[mask_inverse, 'baseline_score']
    inverse_score = 100.0 - (np.maximum(0, user - base) / base) * 100.0
    tv_match_rates.loc[mask_inverse, 'tv_match_rate'] = np.maximum(0, inverse_score)
    
    # Hitung kelengkapan data
    expected_tvs = df_mapping['Sub-test'].nunique()
    actual_tvs = tv_match_rates.groupby('employee_id')['tv_name'].nunique().reset_index()
    actual_tvs.rename(columns={'tv_name': 'actual_tv_count'}, inplace=True)
    actual_tvs['data_completeness'] = (actual_tvs['actual_tv_count'] / expected_tvs) * 100.0
    
    # Agregasi ke level TGV
    tgv_match_rates = tv_match_rates.groupby(['employee_id', 'tgv_name'])['tv_match_rate'].mean().reset_index()
    tgv_match_rates.rename(columns={'tv_match_rate': 'tgv_match_rate'}, inplace=True)
    
    # Hitung tingkat pencocokan akhir
    final_match_df = tgv_match_rates.groupby('employee_id')['tgv_match_rate'].mean().reset_index()
    final_match_df.rename(columns={'tgv_match_rate': 'final_match_rate'}, inplace=True)
    
    # Gabung semua informasi
    df_employees = load_table("employees")
    df_direct = load_table("dim_directorates")
    df_pos = load_table("dim_positions")
    df_grades = load_table("dim_grades")
    
    final_df = pd.merge(tv_match_rates, tgv_match_rates, on=['employee_id', 'tgv_name'], how='left')
    final_df = pd.merge(final_df, final_match_df, on='employee_id', how='left')
    final_df = pd.merge(final_df, actual_tvs[['employee_id', 'data_completeness']], on='employee_id', how='left')
    final_df = pd.merge(final_df, df_employees[['employee_id', 'fullname', 'directorate_id', 'position_id', 'grade_id']], on='employee_id', how='left')
    final_df = pd.merge(final_df, df_direct[['directorate_id', 'name']].rename(columns={'name': 'directorate'}), on='directorate_id', how='left')
    final_df = pd.merge(final_df, df_pos[['position_id', 'name']].rename(columns={'name': 'role'}), on='position_id', how='left')
    final_df = pd.merge(final_df, df_grades[['grade_id', 'name']].rename(columns={'name': 'grade'}), on='grade_id', how='left')
    
    # Pilih dan urutkan kolom
    output_columns = [
        'employee_id', 'fullname', 'directorate', 'role', 'grade',
        'tgv_name', 'Sub-test', 'Meaning', 'Behavior Example', 'Note',
        'baseline_score', 'user_score', 'tv_match_rate', 'tgv_match_rate',
        'final_match_rate', 'data_completeness'
    ]
    
    final_df = final_df[[col for col in output_columns if col in final_df.columns]].copy()
    final_df.rename(columns={'Sub-test': 'tv_name'}, inplace=True)
    final_df.sort_values(
        by=['final_match_rate', 'employee_id', 'tgv_name', 'tv_name'],
        ascending=[False, True, True, True],
        inplace=True,
        na_position='last'
    )
    
    logging.info(f"Matching completed with {len(final_df)} rows")
    return final_df