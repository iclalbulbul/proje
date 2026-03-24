# ön işleme fonksiyonları
from imports import *
import re


def extract_score(value):
    """'deleterious(0.01)' gibi stringlerden sayısal skoru çıkar"""
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


def detect_schema(columns):
    """Veri şemasını otomatik algıla: yarışma (AL_, EK_, ...) veya demo"""
    prefixes = ('AL_', 'AA_', 'EK_', 'CAT_')
    prefix_count = sum(1 for col in columns if any(col.startswith(p) for p in prefixes))
    return 'competition' if prefix_count >= 3 else 'demo'


def _preprocess_demo(data, target_col, panel):
    """Demo veri seti için ön işleme (bilinen sütun isimleri)"""
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

    drop_cols = [col for col in data.columns
                 if col in ['unique_id', 'codons', 'GeneSymbol', 'sift_pred', 'polyphen_pred']]
    data = data.drop(columns=drop_cols, errors='ignore')

    return _common_final_steps(data, target_col, panel)


def _preprocess_competition(data, target_col, panel):
    """Yarışma veri seti için ön işleme (AL_, AA_, EK_, CAT_ prefix'li sütunlar)"""
    # Sütunları prefix'e göre grupla
    al_cols = [c for c in data.columns if c.startswith('AL_')]   # frekans
    ek_cols = [c for c in data.columns if c.startswith('EK_')]   # evrimsel korunum / skorlar
    aa_cols = [c for c in data.columns if c.startswith('AA_')]   # amino asit
    cat_cols = [c for c in data.columns if c.startswith('CAT_')]  # kategorik

    # Frekans ve skor sütunlarını sayısala çevir
    for col in al_cols + ek_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # ID, panel gibi meta sütunları çıkar
    meta_cols = [c for c in data.columns
                 if c not in al_cols + ek_cols + aa_cols + cat_cols and c != target_col]
    data = data.drop(columns=meta_cols, errors='ignore')

    return _common_final_steps(data, target_col, panel)


def _common_final_steps(data, target_col, panel):
    """Her iki şema için ortak: y ayır, impute, one-hot encode"""
    y = data[target_col].copy()
    X = data.drop(columns=[target_col])

    # Sayısal sütunları float'a çevir ve median ile doldur
    numeric_cols = X.select_dtypes(include=['number']).columns
    X[numeric_cols] = X[numeric_cols].astype(float)
    for col in numeric_cols:
        X[col] = X[col].fillna(X[col].median())

    # Kategorik sütunları one-hot encode
    categorical_cols = X.select_dtypes(include=['object']).columns
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

    return X, y, panel


def preprocess_data(data, target_col='label'):
    """Ana ön işleme fonksiyonu — şemayı otomatik algılar"""
    data = data.copy()

    # Panel bilgisini sakla
    panel = data['panel'].copy() if 'panel' in data.columns else None

    schema = detect_schema(data.columns)
    print(f"Algılanan veri şeması: {schema}")

    if schema == 'demo':
        return _preprocess_demo(data, target_col, panel)
    else:
        return _preprocess_competition(data, target_col, panel)