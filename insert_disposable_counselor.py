import json
import os
import mysql.connector

# MySQL connection 설정
cnx = mysql.connector.connect(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                              host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'))

cursor = cnx.cursor()

# client_key와 counselor_key의 초기값 설정
client_key_counter = 1
counselor_key_counter = 1

# JSONL 파일 열기
with open('total_kor_counsel_bot.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        # 각 줄을 json으로 변환
        data = json.loads(line)

        # client_comment 테이블에 insert
        client_query = ("INSERT INTO client_disposable_comment "
                        "(client_key, body) "
                        "VALUES (%s, %s)")
        cursor.execute(client_query, ('cdk_' + str(client_key_counter), data['input']))
        
        # counselor_comment 테이블에 insert 
        counselor_query = ("INSERT INTO counselor_disposable_comment "
                           "(counselor_key, body) "
                           "VALUES (%s, %s)")
        cursor.execute(counselor_query, ('sdk_' + str(counselor_key_counter), data['output']))

        # key counter 값 증가 
        client_key_counter += 1 
        counselor_key_counter += 1 

# commit the transaction and close the connection 
cnx.commit()
cursor.close()
cnx.close()
