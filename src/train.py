#model eğitim scripti
from imports import *
import preprocessing

data = None

#veri yükleme
def load_data(file_path = "./data/demo_final_dataset.csv"):
    global data
    data = pd.read_csv(file_path)
    return data

print(preprocessing.preprocess_data(load_data()).head())