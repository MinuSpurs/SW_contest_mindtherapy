import re
import json
from konlpy.tag import Okt
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import numpy as np
import keras.models
from numpy import argmax
import pickle
from sklearn.preprocessing import LabelEncoder

okt = Okt()
tokenizer  = Tokenizer()

DATA_PATH = 'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/CLEAN_DATA/'
LABEL_DATA = 'nsmc_test_label.npy'

label_data = np.load(open(DATA_PATH + LABEL_DATA,'rb'))

encoder = LabelEncoder()
EMOTION_LABELS = ['분노', '기쁨', '불안', '당황', '슬픔', '상처']
encoder.fit(EMOTION_LABELS)

DATA_CONFIGS = 'data_configs.json'
prepro_configs = json.load(open('C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/CLEAN_DATA/'+DATA_CONFIGS,'r', encoding='utf-8')) 

#데이터 경로 설정
with open('C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/CLEAN_DATA/tokenizer.pickle','rb') as handle:
    word_vocab = pickle.load(handle)

prepro_configs['vocab'] = word_vocab

tokenizer.fit_on_texts(word_vocab)

MAX_LENGTH = 8 #문장최대길이

while True:
    sentence=input('감성분석할 문장을 입력해 주세요.: ')
    if sentence=='끝':
        break
    
    sentence=re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]','',sentence)
    
    stopwords=['은','는','이','가','하','아','것','들',
               '의','있','되','수','보',
               '주','등',] 
    
    sentence=okt.morphs(sentence,stem=True) 
    sentence=[word for word in sentence if not word in stopwords]
    
    vector=tokenizer.texts_to_sequences([sentence])
    
    pad_new=pad_sequences(vector,maxlen=MAX_LENGTH) 
    
    #학습한 모델 불러오기   
    model=keras.models.load_model(r'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/my_models/') 
    model.load_weights(r'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/DATA_OUT/cnn_classifier_kr/weights.h5')
     
    predictions=model.predict(pad_new)
    predicted_index=np.argmax(predictions)

    predicted_label=encoder.inverse_transform([predicted_index])
     
    print("입력 문장의 감정은 {} 입니다.".format(predicted_label[0]))
 