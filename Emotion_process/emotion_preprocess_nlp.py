import numpy as np
import pandas as pd
import re
import json
from konlpy.tag import Okt
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder

DATA_PATH = 'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/DATA/' #데이터 경로 설정
# Excel 파일 읽기
data = pd.read_excel(DATA_PATH+'emotion_copurs_train.xlsx') # your_file.xlsx에 실제 파일 이름 입력

# 사람문장 1, 2, 3을 각각 다른 행으로 만들기 위한 작업
data1 = data[['연령','성별','상황키워드','신체질환','감정_대분류','감정_소분류','사람문장1']].rename(columns={'사람문장1':'document'})
data2 = data[['연령','성별','상황키워드','신체질환','감정_대분류', '감정_소분류', '사람문장2']].rename(columns={'사람문장2':'document'})
data3 = data[['연령','성별','상황키워드','신체질환', '감정_대분류', '감정_소분류', '사람문장3']].rename(columns={'사람문장3':'document'})

# 합치기 (비어있는 문서 행은 제거)
train_data = pd.concat([data1, data2, data3]).dropna(subset=['document'])

encoder = LabelEncoder()
train_data['label'] = encoder.fit_transform(train_data['감정_대분류'])


#전처리 함수 만들기
def preprocessing(review, okt, remove_stopwords = False, stop_words =[]):
  #함수인자설명
  # review: 전처리할 텍스트
  # okt: okt객체를 반복적으로 생성하지 않고 미리 생성 후 인자로 받음
  # remove_stopword: 불용어를 제거할지 여부 선택. 기본값 False
  # stop_words: 불용어 사전은 사용자가 직접 입력, 기본값 빈 리스트

  # 1. 한글 및 공백 제외한 문자 모두 제거
  review_text = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]','',review)
  
  #2. okt 객체를 활용하여 형태소 단어로 나눔
  word_review = okt.morphs(review_text,stem=True)

  if remove_stopwords:
    #3. 불용어 제거(선택)
    word_review = [token for token in word_review if not token in stop_words]
  return word_review


# 전체 텍스트 전처리
stop_words = ['은','는','이','가','하','아','것','들','의','있','되','수','보','주','등','한']
okt = Okt()
clean_train_review = []

for review in train_data['document']:
  # 리뷰가 문자열인 경우만 전처리 진행
  if type(review) == str:
    clean_train_review.append(preprocessing(review,okt,remove_stopwords=True,stop_words= stop_words))
  else:
    clean_train_review.append([]) #str이 아닌 행은 빈칸으로 놔두기

#테스트 리뷰도 동일하게 전처리
# Excel 파일 읽기
data_2 = pd.read_excel(DATA_PATH+'emotion_copurs_validation.xlsx') # your_file.xlsx에 실제 파일 이름 입력

# 사람문장 1, 2, 3을 각각 다른 행으로 만들기 위한 작업
data1 = data_2[['연령','성별','상황키워드','신체질환','감정_대분류','감정_소분류','사람문장1']].rename(columns={'사람문장1':'document'})
data2 = data_2[['연령','성별','상황키워드','신체질환','감정_대분류', '감정_소분류', '사람문장2']].rename(columns={'사람문장2':'document'})
data3 = data_2[['연령','성별','상황키워드','신체질환', '감정_대분류', '감정_소분류', '사람문장3']].rename(columns={'사람문장3':'document'})

# 합치기 (비어있는 문서 행은 제거)
test_data = pd.concat([data1, data2, data3]).dropna(subset=['document'])

# label 컬럼 추가 (여기서는 감정 대분류가 label이 됩니다)
test_data['label'] = encoder.fit_transform(test_data['감정_대분류'])


clean_test_review = []
for review in test_data['document']:
  if type(review) == str:
    clean_test_review.append(preprocessing(review, okt, remove_stopwords=True, stop_words=stop_words))
  else:
    clean_test_review.append([])


# 인덱스 벡터 변환 후 일정 길이 넘어가거나 모자라는 리뷰 패딩처리
tokenizer = Tokenizer()
tokenizer.fit_on_texts(clean_train_review)
train_sequences = tokenizer.texts_to_sequences(clean_train_review)
test_sequences = tokenizer.texts_to_sequences(clean_test_review)

word_vocab = tokenizer.word_index #단어사전형태
MAX_SEQUENCE_LENGTH = 8 #문장 최대 길이

#학습 데이터
train_inputs = pad_sequences(train_sequences,maxlen=MAX_SEQUENCE_LENGTH,padding='post')

#학습 데이터 라벨 벡터화
train_labels = np.array(train_data['label'])

#평가 데이터 
test_inputs = pad_sequences(test_sequences,maxlen=MAX_SEQUENCE_LENGTH,padding='post')
#평가 데이터 라벨 벡터화
test_labels = np.array(test_data['label'])

DEFAULT_PATH  = 'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/' #경로지정
DATA_PATH = 'CLEAN_DATA/' #.npy파일 저장 경로지정
TRAIN_INPUT_DATA = 'nsmc_train_input.npy'
TRAIN_LABEL_DATA = 'nsmc_train_label.npy'
TEST_INPUT_DATA = 'nsmc_test_input.npy'
TEST_LABEL_DATA = 'nsmc_test_label.npy'
DATA_CONFIGS = 'data_configs.json'

data_configs={}
data_configs['vocab'] = word_vocab
data_configs['vocab_size'] = len(word_vocab) + 1

#전처리한 데이터들 파일로저장
import os

if not os.path.exists(DEFAULT_PATH + DATA_PATH):
  os.makedirs(DEFAULT_PATH+DATA_PATH)

#전처리 학습데이터 넘파이로 저장
np.save(open(DEFAULT_PATH+DATA_PATH+TRAIN_INPUT_DATA,'wb'),train_inputs)
np.save(open(DEFAULT_PATH+DATA_PATH+TRAIN_LABEL_DATA,'wb'),train_labels)
#전처리 테스트데이터 넘파이로 저장
np.save(open(DEFAULT_PATH+DATA_PATH+TEST_INPUT_DATA,'wb'),test_inputs)
np.save(open(DEFAULT_PATH+DATA_PATH+TEST_LABEL_DATA,'wb'),test_labels)

#데이터 사전 json으로 저장
json.dump(data_configs, open(DEFAULT_PATH + DATA_PATH + DATA_CONFIGS,'w', encoding='utf-8'), ensure_ascii=False)

# tokenizer 인덱스 값 저장
import pickle
with open(DEFAULT_PATH + DATA_PATH + 'tokenizer.pickle', 'wb') as handle:
    pickle.dump(word_vocab, handle)

