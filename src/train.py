#model eğitim scripti
from imports import *
from sklearn.linear_model import LogisticRegression
from preprocessing import preprocess_data


def load_data(file_path="../data/demo_final_dataset.csv"):
    """Veriyi yükle"""
    data = pd.read_csv(file_path)
    return data


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


def train_xgboost(X_train, y_train, X_test, y_test):
    """XGBoost modeli — sınıf dengesizliği ve early stopping ile"""
    scale_weight = (y_train == 0).sum() / (y_train == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_weight,
        eval_metric='logloss',
        random_state=42,
        early_stopping_rounds=20
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    return model


def save_models(models, path="../models/"):
    """Modelleri kaydet"""
    for name, model in models.items():
        joblib.dump(model, f"{path}{name}.pkl")


if __name__ == "__main__":
    data = load_data()
    X, y, panel = preprocess_data(data)
    X_train, X_test, y_train, y_test, panel_train, panel_test = split_data(X, y, panel)

    lr, rf = train_baseline(X_train, y_train)
    xgb_model = train_xgboost(X_train, y_train, X_test, y_test)

    save_models({"lr_model": lr, "rf_model": rf, "xgb_model": xgb_model})