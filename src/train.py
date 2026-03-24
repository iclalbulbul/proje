#model eğitim scripti
from imports import *
from preprocessing import preprocess_data
from evaluate import evaluate_model, evaluate_by_panel, shap_analysis, plot_precision_recall, optimize_threshold, error_analysis


def load_data():
    """Eğitim ve test verilerini ayrı CSV'lerden yükle"""
    train_path = os.path.join(PROJECT_DIR, "data", "final", "train_dataset.csv")
    test_path = os.path.join(PROJECT_DIR, "data", "final", "test_dataset.csv")
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)
    return train_data, test_data


def split_data(X, y, panel, test_size=0.2, random_state=42):
    """Train/test split — panel bilgisi de bölünür"""
    X_train, X_test, y_train, y_test, panel_train, panel_test = train_test_split(
        X, y, panel, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test, panel_train, panel_test


def train_baseline(X_train, y_train):
    """Baseline modeller: Logistic Regression ve Random Forest"""
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    return lr, rf


def train_xgboost(X_train, y_train, X_test=None, y_test=None):
    """XGBoost modeli — eğitim verisinden validation split ile early stopping"""
    # Eğitim verisinden %15 validation ayır (test verisi ASLA kullanılmaz)
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=1.0,
        eval_metric='logloss',
        random_state=42,
        early_stopping_rounds=30
    )

    model.fit(
        X_tr, y_tr,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    print(f"XGBoost en iyi iterasyon: {model.best_iteration}")
    return model


def save_models(models, path=None):
    if path is None:
        path = os.path.join(PROJECT_DIR, "models")
    os.makedirs(path, exist_ok=True)
    for name, model in models.items():
        joblib.dump(model, os.path.join(path, f"{name}.pkl"))
        
def cross_validate_model(X, y):
    """5-fold stratified cross-validation"""
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=1.0,
        eval_metric='logloss',
        random_state=42
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1_scores = cross_val_score(model, X, y, cv=cv, scoring='f1')
    auc_scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
    
    print(f"F1  — Ortalama: {f1_scores.mean():.4f} ± {f1_scores.std():.4f}")
    print(f"AUC — Ortalama: {auc_scores.mean():.4f} ± {auc_scores.std():.4f}")
    
    return f1_scores, auc_scores


if __name__ == "__main__":
    # Veri yükleme ve ön işleme (ayrı train/test dosyaları)
    train_data, test_data = load_data()
    X_train, y_train, panel_train = preprocess_data(train_data)
    X_test, y_test, panel_test = preprocess_data(test_data)
    
    # One-hot encoding sonrası sütunları hizala (train'de olan ama test'te olmayan sütunlar)
    X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

    # Baseline modeller
    lr, rf = train_baseline(X_train, y_train)
    
    # XGBoost (validation için train'in %15'i ayrılır, test KULLANILMAZ)
    xgb_model = train_xgboost(X_train, y_train)

    # Modelleri kaydet
    save_models({"lr_model": lr, "rf_model": rf, "xgb_model": xgb_model})

    # === Değerlendirme ===
    print("=" * 50)
    print("LOGISTIC REGRESSION")
    print("=" * 50)
    evaluate_model(lr, X_test, y_test)

    print("=" * 50)
    print("RANDOM FOREST")
    print("=" * 50)
    evaluate_model(rf, X_test, y_test)

    print("=" * 50)
    print("XGBOOST")
    print("=" * 50)
    evaluate_model(xgb_model, X_test, y_test)

    # Panel bazlı (sadece XGBoost — asıl model)
    print("=" * 50)
    print("XGBOOST — PANEL BAZLI")
    print("=" * 50)
    evaluate_by_panel(xgb_model, X_test, y_test, panel_test)

    # SHAP analizi
    shap_analysis(xgb_model, X_test, save_path=results_path)

    # Precision-Recall eğrisi
    plot_precision_recall(xgb_model, X_test, y_test, save_path=results_path)
    
    # Eşik optimizasyonu
    print("=" * 50)
    print("EŞİK OPTİMİZASYONU")
    print("=" * 50)
    best_threshold = optimize_threshold(xgb_model, X_test, y_test)
    
    #farklı bir splitle sonuc degisir mi?
    print("=" * 50)
    print("CROSS-VALIDATION (5-Fold)")
    print("=" * 50)
    cross_validate_model(X_train, y_train)
    
    # === Hata Analizi ===
    print("=" * 50)
    print("HATA ANALİZİ")
    print("=" * 50)
    error_analysis(xgb_model, X_test, y_test, panel_test, save_path=results_path)