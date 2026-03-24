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
        pr_auc = average_precision_score(y_test, y_proba)
        print(f"AUC-ROC: {auc:.4f}")
        print(f"PR-AUC:  {pr_auc:.4f}")
    
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
        
def optimize_threshold(model, X_test, y_test, save_path=None):
    """Yüksek recall öncelikli eşik seçimi"""
    y_proba = model.predict_proba(X_test)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
    
    # Recall >= 0.90 olan eşikler arasında en yüksek F1'i bul
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-8)
    
    # Recall en az 0.90 olsun (klinik bağlam: hasta atlanmasın)
    mask = recall[:-1] >= 0.90
    if mask.any():
        best_idx = np.argmax(f1_scores[:-1][mask])
        best_threshold = thresholds[mask][best_idx]
    else:
        best_idx = np.argmax(f1_scores[:-1])
        best_threshold = thresholds[best_idx]
    
    y_pred_custom = (y_proba >= best_threshold).astype(int)
    
    print(f"Seçilen eşik: {best_threshold:.4f}")
    print(f"Bu eşikle F1:     {f1_score(y_test, y_pred_custom):.4f}")
    print(f"Bu eşikle Recall: {(y_pred_custom[y_test == 1].sum() / (y_test == 1).sum()):.4f}")
    print(f"Bu eşikle Precision: {(y_test[y_pred_custom == 1].sum() / y_pred_custom.sum()):.4f}")
    print(f"\nClassification Report (eşik={best_threshold:.4f}):")
    print(classification_report(y_test, y_pred_custom))
    
    return best_threshold

def error_analysis(model, X_test, y_test, panel_test=None, feature_names=None, save_path=None):
    """Yanlış sınıflanan örneklerin analizi"""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # FP ve FN indekslerini bul
    fp_mask = (y_pred == 1) & (y_test.values == 0)
    fn_mask = (y_pred == 0) & (y_test.values == 1)
    correct_mask = y_pred == y_test.values
    
    print(f"Toplam test: {len(y_test)}")
    print(f"Doğru: {correct_mask.sum()} ({correct_mask.mean()*100:.1f}%)")
    print(f"False Positive (FP): {fp_mask.sum()} — benign varyant patojenik dendi")
    print(f"False Negative (FN): {fn_mask.sum()} — patojenik varyant atlandı")
    
    if panel_test is not None:
        print("\n--- Panel Bazlı Hata Oranı ---")
        for panel in sorted(panel_test.unique()):
            idx = panel_test.values == panel
            panel_total = idx.sum()
            panel_fp = (fp_mask & idx).sum()
            panel_fn = (fn_mask & idx).sum()
            panel_error = panel_fp + panel_fn
            print(f"  {panel:20s} | Toplam: {panel_total:4d} | Hata: {panel_error:3d} ({panel_error/panel_total*100:.1f}%) | FP: {panel_fp} | FN: {panel_fn}")
    
    af_cols = [c for c in X_test.columns if 'gnomad' in c.lower() or 'af' in c.lower()]
    if af_cols:
        af_col = af_cols[0]
        print(f"\n--- Popülasyon Frekansı ({af_col}) ve Hata ---")
        af_values = X_test[af_col].copy()
        # nadir (<0.01), orta (0.01-0.05), yaygın (>0.05)
        bins = [-0.001, 0.001, 0.01, 0.05, 1.0]
        labels = ['Çok nadir (<0.001)', 'Nadir (0.001-0.01)', 'Orta (0.01-0.05)', 'Yaygın (>0.05)']
        af_binned = pd.cut(af_values, bins=bins, labels=labels)
        
        for label in labels:
            bin_mask = af_binned == label
            bin_total = bin_mask.sum()
            if bin_total > 0:
                bin_errors = ((fp_mask | fn_mask) & bin_mask.values).sum()
                print(f"  {label:25s} | n={bin_total:4d} | Hata: {bin_errors:3d} ({bin_errors/bin_total*100:.1f}%)")
    
    sift_col = [c for c in X_test.columns if 'sift' in c.lower() and 'score' in c.lower()]
    revel_col = [c for c in X_test.columns if 'revel' in c.lower()]
    
    if sift_col and revel_col:
        sift = X_test[sift_col[0]]
        revel = X_test[revel_col[0]]
        # Çelişki: SIFT tolerant (>0.05) ama REVEL yüksek (>0.5) veya tam tersi
        conflict = ((sift > 0.05) & (revel > 0.5)) | ((sift <= 0.05) & (revel <= 0.5))
        no_conflict = ~conflict
        
        conflict_errors = ((fp_mask | fn_mask) & conflict.values).sum()
        conflict_total = conflict.sum()
        no_conflict_errors = ((fp_mask | fn_mask) & no_conflict.values).sum()
        no_conflict_total = no_conflict.sum()
        
        print(f"\n--- In-Silico Skor Çelişkisi (SIFT vs REVEL) ---")
        if conflict_total > 0:
            print(f"  Çelişkili   | n={conflict_total:4d} | Hata: {conflict_errors:3d} ({conflict_errors/conflict_total*100:.1f}%)")
        if no_conflict_total > 0:
            print(f"  Uyumlu      | n={no_conflict_total:4d} | Hata: {no_conflict_errors:3d} ({no_conflict_errors/no_conflict_total*100:.1f}%)")
    
    fig, axes = plt.subplots(1, 1, figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Benign', 'Patojenik'],
                yticklabels=['Benign', 'Patojenik'], ax=axes)
    axes.set_xlabel('Tahmin')
    axes.set_ylabel('Gerçek')
    axes.set_title('Genel Confusion Matrix')
    plt.tight_layout()
    if save_path:
        plt.savefig(os.path.join(save_path, "confusion_matrix.png"), dpi=300, bbox_inches='tight')
    plt.show()
    
    if panel_test is not None:
        panels = sorted(panel_test.unique())
        fig, axes = plt.subplots(1, len(panels), figsize=(5 * len(panels), 4))
        if len(panels) == 1:
            axes = [axes]
        for ax, panel in zip(axes, panels):
            idx = panel_test.values == panel
            cm_panel = confusion_matrix(y_test[idx], y_pred[idx])
            sns.heatmap(cm_panel, annot=True, fmt='d', cmap='Oranges',
                        xticklabels=['B', 'P'], yticklabels=['B', 'P'], ax=ax)
            ax.set_title(panel)
            ax.set_xlabel('Tahmin')
            ax.set_ylabel('Gerçek')
        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(save_path, "confusion_matrix_panels.png"), dpi=300, bbox_inches='tight')
        plt.show()
    
    return fp_mask, fn_mask