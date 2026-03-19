#değerlendirme fonksiyonları
from imports import *

def evaluate_model(model, X_test, y_test):
    """Model performansını değerlendir"""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    if y_proba is not None:
        auc = roc_auc_score(y_test, y_proba)
        print(f"AUC-ROC: {auc:.4f}")
    
    return y_pred, y_proba

def evaluate_by_panel(model, X_test, y_test, panel_test):
    """Panel bazında değerlendirme"""
    results = []
    for panel in panel_test.unique():
        idx = panel_test == panel
        if idx.sum() > 0:
            print(f"\nEvaluating Panel: {panel}")
            evaluate_model(model, X_test[idx], y_test[idx])
            results.append((panel, idx.sum()))
    return results

def shap_analysis(model, X_data, save_path=None):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_data)
    
    # Global
    shap.summary_plot(shap_values, X_data, plot_type="bar", show=False)
    if save_path:
        plt.savefig(os.path.join(save_path, "shap_global_feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.show()
    
    # Lokal
    shap.waterfall_plot(explainer(X_data)[0], show=False)
    if save_path:
        plt.savefig(os.path.join(save_path, "shap_lokal_aciklama.png"), dpi=300, bbox_inches='tight')
    plt.show()
    
def plot_precision_recall(model, X_test, y_test, save_path=None):
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    if y_proba is not None:
        precision, recall, _ = precision_recall_curve(y_test, y_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, marker='.')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.grid()
        if save_path:
            plt.savefig(os.path.join(save_path, "precision_recall_curve.png"), dpi=300, bbox_inches='tight')
        plt.show()