import numpy as np


DATA_PATH = 'C:/Users/gapbu/Desktop/SW_contest_mindtherapy/Emotion_process/CLEAN_DATA/'

LABEL_DATA = 'nsmc_test_label.npy'  # 실제 파일 이름으로 변경하세요.

labels = np.load(open(DATA_PATH + LABEL_DATA,'rb'))
unique_labels = np.unique(labels)
print("Unique labels in the dataset: ", unique_labels)