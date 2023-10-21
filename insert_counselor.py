import json
import os
import mysql.connector

# MySQL connection 설정
cnx = mysql.connector.connect(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                              host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'))

cursor = cnx.cursor()

# thread_key 초기값 설정
counselor_key_counter = 1
client_key_counter = 1

# JSONL 파일 열기
with open('total_kor_multiturn_counsel_bot.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)

        last_speaker = None
        
        for i in range(len(data)):
            utterance = data[i]['utterance']
            speaker = data[i]['speaker']

            # leaf_node 값 결정 (마지막 발언일 경우)
            if last_speaker and last_speaker != speaker:
                cursor.execute(update_query, params)

            leaf_node = 0 

            if speaker == '상담사':
                # counselor_comment 테이블에 insert 
                counselor_query = ("INSERT INTO counselor_comment "
                                   "(counselor_key, body, is_leaf_node) "
                                   "VALUES (%s, %s, %s)")
                
                cursor.execute(counselor_query,
                               ('sk_' + str(counselor_key_counter),
                                utterance,
                                leaf_node))
                
                update_query="UPDATE counselor_comment SET is_leaf_node=1 WHERE counselor_key=%s"
                params=('sk_' + str(counselor_key_counter-1),)
                        
                counselor_key_counter += 1
                
                
            elif speaker == '내담자':
                # client_comment 테이블에 insert 
                client_query=("INSERT INTO client_comment "
                              "(client_key, body, is_leaf_node) "
                              "VALUES (%s, %s, %s)")
                
                cursor.execute(client_query,
                               ('ck_' + str(client_key_counter),
                                utterance,
                                leaf_node))

                update_query="UPDATE client_comment SET is_leaf_node=1 WHERE client_key=%s"
                params=('ck_' + str(client_key_counter-1),)

                client_key_counter += 1 


        # 마지막 발언을 리프노드로 설정하는 쿼리를 추가합니다.
        if speaker == '상담사':
           update_query="UPDATE counselor_comment SET is_leaf_node=1 WHERE counselor_key=%s"
           params=('sk_' + str(counselor_key_counter-1),)
        elif speaker == '내담자':
           update_query="UPDATE client_comment SET is_leaf_node=1 WHERE client_key=%s"
           params=('ck_' + str(client_key_counter-1),)

        cursor.execute(update_query, params)

# commit the transaction and close the connection 
cnx.commit()
cursor.close()
cnx.close()
