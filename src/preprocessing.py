#ön işleme fonksiyonları
from imports import *

def preprocess_data(data):
    # Eksik değerleri doldurma
    data = data.fillna(data.median())
    
    # Kategorik değişkenleri sayısal hale getirme
    data = pd.get_dummies(data, drop_first=True)
    
    return data