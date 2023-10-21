import os
import mysql.connector

# MySQL connection 설정
cnx = mysql.connector.connect(user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                              host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'))

cursor = cnx.cursor()

# 삽입된 행의 수 세기
inserted_rows = 0

# 초기 상담자와 고객의 키 설정 (처음 시작은 ck_1 -> sk_2 -> ck_2 패턴)
client_key_index = 1
counselor_key_index = 2

while True:
    # client_comment 테이블에서 필요한 데이터 가져오기 (마지막 발언 포함)
    cursor.execute(f"SELECT client_key FROM client_comment WHERE client_key IN ('ck_{client_key_index}', 'ck_{client_key_index + 1}') ORDER BY CAST(SUBSTRING(client_key, 4) AS UNSIGNED) ASC")
    clients = cursor.fetchall()

    # counselor_comment 테이블에서 필요한 데이터 가져오기 (마지막 발언 제외)
    cursor.execute(f"SELECT counselor_key, is_leaf_node FROM counselor_comment WHERE counselor_key='sk_{counselor_key_index}'")
    counselors = cursor.fetchall()

     # 다음 루프를 위해 인덱스 업데이트 
    if counselors[0][1] == 1:   # If the current counselor's comment is a leaf node,
         client_key_index += 1   # skip the next client's comment.
         counselor_key_index +=2 
    else:
         client_key_index += 1 
         counselor_key_index += 1 

     # thread 테이블에 데이터 삽입하기 위한 조건 확인하기 (반복문 종료 조건)
    if len(clients) < 2 or len(counselors) < 1:
        break

    # thread 테이블에 데이터 삽입
    thread_query=("INSERT INTO thread "
                  "(client_key_1, counselor_key, client_key_2) "
                  "VALUES (%s, %s, %s)")
    
    params=(clients[0][0], counselors[0][0], clients[1][0])
    
    cursor.execute(thread_query, params)

     # 삽입된 행의 수 업데이트 및 메시지 출력
    inserted_rows += 1
    if inserted_rows % 100 == 0:
         print(f'{inserted_rows} rows have been inserted.')


# commit the transaction and close the connection 
cnx.commit()
cursor.close()
cnx.close()
