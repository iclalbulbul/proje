#model eğitim scripti
from imports import *
from preprocessing import preprocess_data

data = None

#veri yükleme
def load_data(file_path = "./data/demo_final_dataset.csv"):
    global data
    data = pd.read_csv(file_path)
    return data

data = load_data()
X, y, panel = preprocess_data(data)