# ön işleme fonksiyonları
from imports import *
import re

def extract_score(value):
    if pd.isna(value) or value == '-':
        return np.nan
    match = re.search(r'\(([\d.]+)\)', str(value))
    if match:
        return float(match.group(1))
    return np.nan

def split_amino_acids(value):
    if pd.isna(value) or value == '-':
        return np.nan, np.nan
    parts = str(value).split('/')
    return parts[0] if len(parts) > 0 else np.nan, parts[1] if len(parts) > 1 else np.nan

def preprocess_data(data, target_col='label'):
    data = data.copy()
    
    data = data.replace('-', np.nan)
    
    force_numeric = ['cadd_phred', 'cadd_raw', 'revel', 'gnomad_af', 
                 'gnomadg_af', 'alphamissense_score']
    
    for col in force_numeric:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    if 'sift_score' in data.columns:
        data['sift_score'] = data['sift_score'].apply(extract_score)
    if 'polyphen_score' in data.columns:
        data['polyphen_score'] = data['polyphen_score'].apply(extract_score)
    
    if 'amino_acids' in data.columns:
        data[['ref_amino', 'alt_amino']] = data['amino_acids'].apply(
            lambda x: pd.Series(split_amino_acids(x))
        )
        data = data.drop('amino_acids', axis=1)
        
    panel = data['panel'].copy() if 'panel' in data.columns else None
    
    drop_cols = [col for col in data.columns 
                 if col in ['unique_id', 'codons', 'GeneSymbol', 'sift_pred', 'polyphen_pred', 'panel'] 
                 or col.startswith('panel')]
    data = data.drop(columns=drop_cols, errors='ignore')
    
    y = data[target_col].copy()
    X = data.drop(columns=[target_col])
    
    numeric_cols = X.select_dtypes(include=['number']).columns
    X[numeric_cols] = X[numeric_cols].astype(float)
    
    for col in numeric_cols:
        X[col] = X[col].fillna(X[col].median())
    
    categorical_cols = X.select_dtypes(include=['object']).columns
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    return X, y, panel