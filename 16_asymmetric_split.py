import pandas as pd
import numpy as np
import os

# Proje kök dizinini belirle
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(PROJECT_DIR, "data", "demo_final_dataset.csv")
OUTPUT = os.path.join(PROJECT_DIR, "data", "final")
os.makedirs(OUTPUT, exist_ok=True)

df = pd.read_csv(INPUT)

print(f"Toplam veri: {len(df)}")
print(f"Panel dagilimi:\n{df.groupby(['panel', 'label']).size()}\n")

egitim_listesi = []
test_listesi = []

for panel in df['panel'].unique():
    panel_df = df[df['panel'] == panel].copy()
    
    patojenik = panel_df[panel_df['label'] == 1]
    benign = panel_df[panel_df['label'] == 0]
    
    # Egitim: patojenikin %80i, benignin %40i
    # Test: patojenikin %20si, benignin %60i
    # Bu sekilde egitimde P agirlikli, testte B agirlikli olur
    
    p_egitim = patojenik.sample(frac=0.80, random_state=42)
    p_test = patojenik.drop(p_egitim.index)
    
    b_egitim = benign.sample(frac=0.40, random_state=42)
    b_test = benign.drop(b_egitim.index)
    
    egitim_listesi.append(pd.concat([p_egitim, b_egitim]))
    test_listesi.append(pd.concat([p_test, b_test]))
    
    print(f"{panel}:")
    print(f"  Egitim → {len(p_egitim)} P / {len(b_egitim)} B")
    print(f"  Test   → {len(p_test)} P / {len(b_test)} B")

egitim = pd.concat(egitim_listesi, ignore_index=True).sample(frac=1, random_state=42)
test = pd.concat(test_listesi, ignore_index=True).sample(frac=1, random_state=42)

egitim.to_csv(os.path.join(OUTPUT, "train_dataset.csv"), index=False)
test.to_csv(os.path.join(OUTPUT, "test_dataset.csv"), index=False)

print(f"\nEgitim toplam: {len(egitim)} ({(egitim['label']==1).sum()} P / {(egitim['label']==0).sum()} B)")
print(f"Test toplam:   {len(test)} ({(test['label']==1).sum()} P / {(test['label']==0).sum()} B)")
print("\nTamamlandi.")