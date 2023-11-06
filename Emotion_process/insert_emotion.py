import re
import json
from konlpy.tag import Okt
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import numpy as np
import keras.models
from numpy import argmax
import pickle
import mysql.connector
import os
from sklearn.preprocessing import LabelEncoder

# MySQL 연결 설정하기 (여기에는 실제 연결 정보를 입력해야 합니다.)
cnx = mysql.connector.connect(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                              host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'))

okt = Okt()
tokenizer  = Tokenizer()

DATA_PATH = 'C:/Users/82107/Desktop/Study/SW_contest_mindtherapy/Emotion_process/CLEAN_DATA/'
LABEL_DATA = 'nsmc_test_label.npy'

label_data = np.load(open(DATA_PATH + LABEL_DATA,'rb'))

encoder = LabelEncoder()
EMOTION_LABELS_KR = ['분노', '기쁨', '불안', '당황', '슬픔', '상처']
EMOTION_LABELS_ENG = ['angry','happy','anxious','embarrassed','sad','hurt']

# 감정 한글 라벨과 영문 라벨 매핑 딕셔너리 생성 
emotion_dict_kr_to_eng=dict(zip(EMOTION_LABELS_KR, EMOTION_LABELS_ENG))

encoder.fit(EMOTION_LABELS_KR)

DATA_CONFIGS = 'data_configs.json'
prepro_configs = json.load(open('C:/Users/82107/Desktop/Study/SW_contest_mindtherapy/Emotion_process/CLEAN_DATA/'+DATA_CONFIGS,'r', encoding='utf-8')) 

#데이터 경로 설정
with open('C:/Users/82107/Desktop/Study/SW_contest_mindtherapy/Emotion_process/CLEAN_DATA/tokenizer.pickle','rb') as handle:
    word_vocab = pickle.load(handle)

prepro_configs['vocab'] = word_vocab

tokenizer.fit_on_texts(word_vocab)

select_cursor = cnx.cursor(buffered=True)
update_cursor = cnx.cursor()

# client_comment 테이블에서 데이터 조회하기
select_query = "SELECT client_key, body FROM client_disposable_comment"
select_cursor.execute(select_query)

results = select_cursor.fetchall()

MAX_LENGTH = 8 #문장최대길이

#학습한 모델 불러오기   
model=keras.models.load_model(r'C:/Users/82107/Desktop/Study/SW_contest_mindtherapy/Emotion_process/my_models/') 
model.load_weights(r'C:/Users/82107/Desktop/Study/SW_contest_mindtherapy/Emotion_process/DATA_OUT/cnn_classifier_kr/weights.h5')

for (client_key, body) in results:
    
    sentence=re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]','',body)
    
    stopwords=['은','는','이','가','하','아','것','들',
               '의','있','되','수','보',
               '주','등',] 
    
    sentence=okt.morphs(sentence,stem=True) 
    sentence=[word for word in sentence if not word in stopwords]
    
    vector=tokenizer.texts_to_sequences([sentence])
    
    pad_new=pad_sequences(vector,maxlen=MAX_LENGTH) 

    predictions = model.predict(pad_new)
     
    predicted_index=np.argmax(predictions)
    predicted_label_kr=encoder.inverse_transform([predicted_index])[0]
    
    # 딕셔너리를 사용해 한글 감정 라벨을 영문으로 변환합니다.
    predicted_label_eng=emotion_dict_kr_to_eng[predicted_label_kr]
     
     # 결과 출력 및 데이터베이스 업데이트 
    print("입력 문장의 감정은 {} 입니다.".format(predicted_label_eng))
    
     # 감성 분석 결과를 emotion 열에 업데이트하기  
    update_query="UPDATE client_disposable_comment SET emotion=%s WHERE client_key=%s"
    update_cursor.execute(update_query,(predicted_label_eng,client_key))
 
cnx.commit()  

select_cursor.close()
update_cursor.close()
cnx.close()