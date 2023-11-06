# SW_contest_mindtherapy

## SW_contest

본 데이터셋의 상담 내용은 전량 OpenAI API를 통해 구축되었습니다.
딥러닝에 필요한 데이터셋 중 자연어를 긍정과 부정인지 구별해주는 데이터는 공개된 영화 리뷰들, 자연어를 6가지 감정으로 나눠주는 데이터는 AI hub에 공개되어 있는 상담 내용을 통해 학습을 진행했다.


## Data_insert

### total_kor_counsel_bot.jsonl

* 총 13,234 싱글턴 장문 데이터
* input: 고민 내용
* output: 상담사 답변


### total_kor_multiturn_counsel_bot.jsonl

* 총 8,731 멀티턴 대화 데이터
* speaker: 발화자
* utterance: 발화 내용


### DB 환경

* 먼저 MYSQL에 테이블들을 생성해서 싱글턴 대화와 멀티턴 대화를 상담자와 내담자를 구분지어 INSERT해주기 위해 jsonl파일을 불러오는 코드를 작성했다.
각각의 테이블들은 자동으로 데이터를 INSERT 했을 때 PRIMARY_KEY 역할을 하는 id가 주어진다.


### insert_disposable_counselor.py

* 싱글턴 장문 데이터를 DB에 INSERT 해주기 위한 코드다.
* jsonl파일의 각각의 줄을 json으로 변환해준다.
* 싱글턴 장문 데이터는 client_disposable_comment와 counselor_disposable_comment 테이블 두개로 나누어 client_comment에는 내담자의 대화를, counselor_comment에는 상담자의 대화를 INSERT 해주었다.
* PRIMARY_KEY는 client_disposable_comment에서는 client_disposable_key를 줄인 cdk_1, cdk_2 ... cdk_x 로 주어지고 counselor_disposable_comment는 sdk_1, sdk_2 ... sdk_x로 주어진다.


### insert_counselor.py

* 멀티턴 데이터를 DB에 INSERT 해주기 위한 코드다.
* jsonl파일의 각각의 줄을 json으로 변환해준다.
* 멀티턴 데이터들은 한 대화 쓰레드에 여러번의 대화가 오고가기 때문에 하나의 대화 쓰레드가 끝날 때 마다 leaf_node임을 알려주기 위하여 데이터 테이블에 is_leaf_node를 추가했다.
* 멀티턴 데이터는 client_comment와 counselor_comment 테이블 두개로 나누어 진행한다.
* PRIMARY_KEY는 lient_comment에서는 client_key를 줄인 ck_1, ck_2 ... ck_x 로 주어지고 counselor_comment는 sk_1, sk_2 ... sk_x로 주어진다.
* 한 개의 대화 쓰레드에서 마지막 발언인 것을 확인하면 is_leaf_node에 1을 넣어주어 이 발언이 쓰레드의 마지막 발언임을 표시해준다.


### insert_thread.py

* 멀티턴 데이터를 통해 ( 내담자의 대화 -> 상담사의 발언 -> 내담자의 반응 )을 통해 내담자의 감정이 어떻게 바뀌는지 보기 위해 데이터를 triplet 형식으로 삽입한다.
* thread 테이블은 client_key_1, counselor_key, client_key_2 컬럼들로 구성되어 있으며, 이 데이터들은 모두 상담자의 인사로 시작이 되기 때문에 처음 상담자의 대화는 제외하고 thread 테이블에 INSERT 해준다.
* 각기 다른 테이블에서 값들을 불러와 INSERT 해주는 것이기 때문에 순서가 꼬이지 않게 예외처리를 해준다.



## pos_neg_nlp

### preprocess_nlp.py

* 영화 리뷰 데이터를 학습시킬 수 있게 전처리를 해준다.
* 한글과 공백을 제외한 문자를 모두 제거하고, okt 객체를 활용하여 문장을 형태소 단위로 나눠준다.
* 리뷰가 문자열일 때만 전처리를 진행하도록 해준다.
* 데이터의 라벨을 벡터화 해줘 데이터를 저장시켜준다.

### train_nlp.py

* cnn 분류기를 통해 긍정, 부정 라벨링이 되어있는 영화 리뷰 트레이닝 데이터를 학습한다.
* 그 가중치를 파일로 저장시킨다.


### test_nlp.py

* 학습한 트레이닝 데이터를 통해 테스트를 해서 정확도를 구한다.


### insert_is_pos.py

* client_comment 테이블에 is_pos라는 컬럼을 추가해준다.
* client_comment 테이블에서 내담자의 상담 내용을 조회하여 그 내용이 긍정인지 부정인지 판단한다.
* 긍정이면 is_pos에 1을, 부정이면 0을 INSERT 해준다.



## Emotion_process

### emotion_preprocess_nlp.py

* 6가지 감정이 라벨링 되어있는 AI hub에 공개되어 있는 상담 내용들을 preprocess_nlp.py와 같은 방식으로 전처리 해준다.


### emotion_train_nlp.py

* 앞서 train_nlp.py와 같은 분류모델을 사용하지만 다중 클래스 분류 문제이므로 손실 함수를 categorical_crossentropy로 설정해준다.
* 이하 내용은 train_nlp.py와 같다.
