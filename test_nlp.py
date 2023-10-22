# 학습된 모델 테스트
import numpy as np
from keras.utils import pad_sequences
import keras
import pickle
DATA_PATH = 'C:/Users/82107/Desktop/Study/SW_Contest/CLEAN_DATA/' #데이터 경로 설정
INPUT_TEST_DATA = 'nsmc_test_input.npy'
LABEL_TEST_DATA = 'nsmc_test_label.npy'
SAVE_FILE_NM = 'weights.h5'

test_input = np.load(open(DATA_PATH+INPUT_TEST_DATA,'rb'))
test_input = pad_sequences(test_input,maxlen=test_input.shape[1])
test_label_data = np.load(open(DATA_PATH + LABEL_TEST_DATA, 'rb'))

model = keras.models.load_model(r'C:/Users/82107/Desktop/Study/SW_Contest/my_models/') 
model.load_weights(r'C:/Users/82107/Desktop/Study/SW_Contest/DATA_OUT/cnn_classifier_kr/weights.h5') 
model.evaluate(test_input, test_label_data)