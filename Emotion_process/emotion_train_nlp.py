# 학습 데이터 불러오기
import tensorflow as tf
from keras.utils import pad_sequences
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import layers
import numpy as np
import pandas as pd
import os
import json
from keras.models import save_model
from keras.utils import to_categorical

#학습 설정 - loss를 categorical_crossentropy로 변경하고 label을 원-핫 인코딩으로 변환합니다.

#전처리 데이터 불러오기
DATA_PATH = 'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/CLEAN_DATA/' #데이터 경로 설정
DATA_OUT = 'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/DATA_OUT/' #데이터 경로 설정
INPUT_TRAIN_DATA = 'nsmc_train_input.npy'
LABEL_TRAIN_DATA = 'nsmc_train_label.npy'
DATA_CONFIGS = 'data_configs.json'

train_input = np.load(open(DATA_PATH + INPUT_TRAIN_DATA,'rb'))
train_input = pad_sequences(train_input,maxlen=train_input.shape[1])
train_label = np.load(open(DATA_PATH + LABEL_TRAIN_DATA,'rb'))
prepro_configs = json.load(open(DATA_PATH+DATA_CONFIGS,'r', encoding='utf-8'))

#파라미터 세팅
model_name= 'cnn_classifier_kr'
BATCH_SIZE = 512
NUM_EPOCHS = 10
VALID_SPLIT = 0.1
MAX_LEN = train_input.shape[1]

kargs={'model_name': model_name,
        'vocab_size':prepro_configs['vocab_size'],
        'embbeding_size':128, 
        'num_filters':100,
        'dropout_rate':0.5, 
        'hidden_dimension':250,
        'output_dimension':6} # 라벨의 수에 맞게 변경

#모델 생성
class CNNClassifier(tf.keras.Model):

  def __init__(self, **kargs):
    super(CNNClassifier, self).__init__(name=kargs['model_name'])
    self.embedding = layers.Embedding(input_dim=kargs['vocab_size'], output_dim=kargs['embbeding_size'])
    self.conv_list = [layers.Conv1D(filters=kargs['num_filters'], kernel_size=kernel_size, padding='valid',activation=tf.keras.activations.relu,kernel_constraint=tf.keras.constraints.MaxNorm(max_value=3)) for kernel_size in [3,4,5]]
    self.pooling = layers.GlobalMaxPooling1D()
    self.dropout = layers.Dropout(kargs['dropout_rate'])
        
    self.fc1 = layers.Dense(units=kargs['hidden_dimension'],
                            activation=tf.keras.activations.relu,
                            kernel_constraint=tf.keras.constraints.MaxNorm(max_value=3.))
        
    # softmax 활성화 함수 사용 및 라벨의 수에 맞게 출력 차원 변경                                
    self.fc2=layers.Dense(units=kargs["output_dimension"],
                          activation="softmax",
                          kernel_constraint=tf.keras.constraints.MaxNorm(max_value=3.))

  def call(self,x):
    x=self.embedding(x)
    x=self.dropout(x)
    x=tf.concat([self.pooling(conv(x)) for conv in self.conv_list],axis=-1)
    x=self.fc1(x)
    x=self.fc2(x)

    return x

train_label_onehot=to_categorical(train_label)

model=CNNClassifier(**kargs)

model.compile(optimizer="adam",
              loss="categorical_crossentropy", # 다중 클래스 분류 문제이므로 손실 함수를 categorical_crossentropy로 설정합니다.
              metrics=["accuracy"])

earlystop_callback=EarlyStopping(monitor="val_accuracy",min_delta=0.0001,patience=2)

checkpoint_path=os.path.join(DATA_OUT,model_name,"weights.h5")
checkpoint_dir=os.path.dirname(checkpoint_path)

if os.path.exists(checkpoint_dir):
    print(f"{checkpoint_dir} -- Folder already exists\n")
else:
    os.makedirs(checkpoint_dir,exist_ok=True)
    print(f"{checkpoint_dir} -- Folder create complete\n")

cp_callback=ModelCheckpoint(checkpoint_path,
                            monitor="val_accuracy",
                            verbose=1,
                            save_best_only=True,
                            save_weights_only=True)

history=model.fit(train_input,train_label_onehot,
                  batch_size=BATCH_SIZE,
                  epochs=NUM_EPOCHS,
                  validation_split=VALID_SPLIT,
                  callbacks=[earlystop_callback,cp_callback])

# 모델 저장하기
save_model(model,'C:/Users/82107/Desktop/Study/SW_Contest/Emotion_process/my_models/') #저장폴더지정