import psycopg2
from datetime import date
import hashlib

con = None
current_id, current_role = None, None

def print_boundary():
    print("-" * 20)
def login():
    global con
    global current_id
    global current_role

    input_id = input("ID: ")
    input_password = input("Password: ")

    cur = con.cursor()

    try:
        # 입력 받은 ID와 Password를 사용하여 쿼리 실행
        cur.execute("SELECT role, password FROM Register WHERE ID = %s", (input_id, ))

        # 결과 가져오기
        result = cur.fetchone()

        hashed_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()

        if result and hashed_password == result[1]:
            current_role = result[0]
            cur.execute(f"SELECT id, name FROM \"{current_role}\" WHERE ID = %s", (input_id,))
            result = cur.fetchone()
            current_id = result[0]
            current_name = result[1]
            print("로그인 성공! Hi,", current_name, sep=" ")
            con.close()
            con = psycopg2.connect(
                database='sample2023',
                user=input_id.lower(),
                password=input_password,
                host='::1',
                port='5432'
            )
            return True
        else:
            print("로그인 실패. ID 또는 비밀번호가 일치하지 않습니다.")
            return False

    except psycopg2.Error as e:
        print(f"데이터베이스 오류: {e}")
        return False

    finally:
        # 연결과 커서 닫기
        cur.close()

def create_user(user_id, password):
    try:
        global con

        # 커서 생성
        cur = con.cursor()
        # 새로운 사용자 생성
        cur.execute(f"CREATE USER {user_id} WITH PASSWORD '{password}';")
    except Exception as e:
        print(f"Error: {e}")

def register_user(cursor, input_id, input_password, input_nickname, email, role, inspector_introduce=None):
    hashed_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
    create_user(input_id, input_password)
    if role == 1:  # User
        cursor.execute("INSERT INTO \"user\" (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, hashed_password, "user"))
        cursor.execute(f"GRANT \"user\" TO {input_id}")
        # cursor.execute(f"GRANT SELECT, INSERT ON TABLE market, product, enterprise, inspector TO {input_id}")
        # cursor.execute(f"GRANT ALL ON TABLE wish, \"User\", request TO {input_id}")
        # cursor.execute(f"GRANT DELETE, UPDATE ON TABLE register TO {input_id}")
    elif role == 2:  # Enterprise
        cursor.execute("INSERT INTO Enterprise (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, hashed_password, "enterprise"))
        cursor.execute(f"GRANT \"enterprise\" TO {input_id}")
    elif role == 3:  # Inspector
        cursor.execute("INSERT INTO Inspector (ID, name, e_mail, introduce) VALUES (%s, %s, %s, %s)",
                       (input_id, input_nickname, email, inspector_introduce))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, hashed_password, "inspector"))
        cursor.execute(f"GRANT \"inspector\" TO {input_id}")

    con.commit()


def register():
    global con
    cur = con.cursor()

    print_boundary()
    print("아래의 회원가입 정보를 입력해주세요.")
    while True:
        input_id = input("ID: ")
        cur.execute("SELECT * FROM Register WHERE ID = %s", (input_id,))
        if cur.fetchone() is None:
            break
        print("이미 사용중인 ID 입니다.")

    while True:
        input_password = input("Password: ")
        if len(input_password) >= 8:
            break
        print("비밀번호는 8자 이상 입력 해주세요.")

    while True:
        input_nickname = input("Nickname: ")
        if len(input_nickname) < 20:
            break
        print("닉네임은 20자 이내로 입력 해주세요.")

    while True:
        input_email = input("E-mail: ")
        if len(input_email) < 30:
            break
        print("e-mail은 30자 이내로 입력 해주세요.")
        break

    while True:
        input_role = int(input("Select Your Account Type\n1. User\n2. Enterprise\n3. Inspector\nSelect: "))
        if 1 <= input_role <= 3:
            inspector_introduce = None
            if input_role == 3:
                inspector_introduce = input("Introduce your information.\nInput: ")
            break
        print("1~3중에 선택 해주세요.")

    try:
        register_user(cur, input_id, input_password, input_nickname, input_email, input_role, inspector_introduce)
        print("회원 가입이 완료되었습니다.")
    except psycopg2.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        con.commit()  # 변경 사항 커밋

    print_boundary()
    cur.close()
    return True

def manage():
    print("Dev...")

def enter():
    while True:
        print_boundary()
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print_boundary()
        login_type = int(input("Select: "))
        if login_type == 1:
            if login():
                break
        elif login_type == 2:
            register()
        elif login_type == 3:
            return False
        elif login_type == 99999:
            # 숨겨진 관리자 모드
            manage()
            break
        else:
            print("잘못된 입력입니다.")

    return True

def print_user_menu():
    print_boundary()
    print("1. 시장조회")
    print("2. 물품구매")
    print("3. 점검요청")
    print("4. 구매 현황 조회")
    print("5. 점검 현황 조회")
    print("6. 계정 설정")
    print("7. 로그아웃")
    print_boundary()

def print_enterprise_menu():
    print_boundary()
    print("1. 시장 조회")
    print("2. 판매 물품 등록")
    print("3. 판매 현황 조회")
    print("4. 점검 요청")
    print("5. 점검 현황 조회")
    print("6. 계정 설정")
    print("7. 로그아웃")
    print_boundary()
def print_inspector_menu():
    print_boundary()
    print("1. 시장 조회")
    print("2. 점검 리스트")
    print("3. 점검 완료 처리")
    print("4. 소개 변경")
    print("5. 계정 설정")
    print("6. 로그아웃")
    print_boundary()

def print_error_input():
    print("잘못된 입력입니다.")

def print_logout():
    print("로그아웃 하였습니다.")

def change_nickname(cur):
    input_nickname = input("변경할 닉네임: ")
    if len(input_nickname) < 20:
        cur.execute(f"UPDATE \"{current_role}\" SET name = \'{input_nickname}\' WHERE id = \'{current_id}\'")
        con.commit()
        print("닉네임 변경 완료!")
        return True

    return False

def confirm_password(cur):
    input_password = input("현재 비밀번호: ")

    hashed_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
    cur.execute("SELECT * FROM Register WHERE ID = %s AND password = %s", (current_id, hashed_password))
    result = cur.fetchone()
    if result:
        return True
    else:
        return False

def account_setting(cur):
    global con
    while True:
        print_boundary()
        print("1. 닉네임 변경")
        print("2. 비밀번호 변경")
        print("3. 계정 삭제")
        print("4. 이전")
        print_boundary()
        input_select = int(input("Select: "))
        if input_select == 1:
            if change_nickname(cur):
                break
            else:
                print("닉네임 변경 실패")
        elif input_select == 2:
            if confirm_password(cur):
                input_password = input("새로운 비밀번호: ")
                if len(input_password) >= 8:
                    hashed_password = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
                    cur.execute(f"UPDATE register SET password = \'{hashed_password}\' WHERE id = \'{current_id}\'")
                    cur.execute(f"ALTER USER {current_id} WITH PASSWORD %s", (input_password,))
                    con.commit()
                else:
                    print("비밀번호는 8자 이상 입력 해주세요.")
            else:
                print("잘못된 비밀번호입니다.")
        elif input_select == 3:
            if confirm_password(cur):
                input_reconfirm = input("정말로 삭제 하시겠습니까? (Y/N)")
                if input_reconfirm == 'Y':
                    con.close()
                    con = psycopg2.connect(
                        database='sample2023',
                        user='db2023',
                        password='db!2023',
                        host='::1',
                        port='5432'
                    )
                    cur = con.cursor()
                    cur.execute(f"DELETE FROM register WHERE id = \'{current_id}\'")
                    cur.execute(f"DELETE FROM \"{current_role}\" WHERE id = \'{current_id}\'")
                    cur.execute(f"DROP USER {current_id}")
                    con.commit()
                    print("계정이 삭제되었습니다.")
                    return False
                else:
                    print("계정 삭제를 취소합니다.")
            else:
                print("잘못된 비밀번호입니다.")
        elif input_select == 4:
            break
        else:
            print_error_input()

    return True

def print_market(cur):
    sql_query = """
                    SELECT E.name, P.product_name, P.product_description, P.price, P.category, P.certification, M.enrollment_date, P.product_id
                    FROM Product P  
                    JOIN Market M ON P.product_id = M.product_id
                    JOIN Enterprise E ON P.enterprise_id = E.ID;
                """
    cur.execute(sql_query)
    result = cur.fetchall()

    print(f"|{'제품 ID'.center(15)}|{'회사명'.center(15)}|{'상품명'.center(15)}|{'상품 설명'.center(15)}|{'가격'.center(15)}|{'카테고리'.center(15)}|{'인증'.center(15)}|{'등록일자'.center(15)}|")
    for record in result:
        print(f"|{record[7].center(15)}|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{str(record[3]).center(15)}|{record[4].center(15)}|{str(record[5]).center(15)}|{str(record[6]).center(15)}|")

def register_product(cur):
    cur.execute("SELECT product_id FROM product")
    result = cur.fetchall()
    if len(result) == 0:
        product_id = 1
    else:
        cur.execute("SELECT MAX(CAST(product_id AS INT)) FROM product")
        result = cur.fetchone()
        product_id = result[0] + 1

    enterprise_id = current_id
    product_name = input("제품 이름: ")
    product_description = input("제품 설명: ")
    print("---------카테고리---------")
    print("1. 식품")
    print("2. 전자제품")
    print("3. 생활용품")
    print("-------------------------")
    category = None
    while True:
        category = int(input("Select: "))
        if 1 <= category <= 3:
            if category == 1:
                category = "food"
            elif category == 2:
                category = "electronic"
            else:
                category = "household"
            break
        print_error_input()
    price = int(input("가격: "))
    cur.execute("INSERT INTO product (product_id, enterprise_id, product_name, product_description, category, price) VALUES (%s, %s, %s, %s, %s, %s)", (product_id, enterprise_id, product_name, product_description, category, price))
    cur.execute("INSERT INTO market (product_id, enrollment_date) VALUES (%s, %s)", (product_id, date.today()))
    con.commit()
    print("제품 등록 완료")

def buy_product(cur):
    print_boundary()
    select_product_id = input("구매하려는 상품 ID를 입력하세요.\nSelect: ")
    sql_query = f"""
                        SELECT E.name, P.product_name, P.product_description, P.price, P.category, P.certification, M.enrollment_date, P.product_id
                        FROM Product P  
                        JOIN Market M ON P.product_id = M.product_id
                        JOIN Enterprise E ON P.enterprise_id = E.ID
                        WHERE P.product_id = \'{(select_product_id)}\' and P.phase_owner IS NULL;
                    """
    cur.execute(sql_query)
    result = cur.fetchall()
    if len(result) == 1:        # 해당 제품이 있다면
        record = result[0]
        print(f"|{record[7].center(15)}|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{str(record[3]).center(15)}|{record[4].center(15)}|{str(record[5]).center(15)}|{str(record[6]).center(15)}|")
        select_confirm = input("구매하려는 상품이 맞습니까? (Y/N): ")
        if select_confirm == 'Y':
            cur.execute(f"UPDATE Product SET phase_owner = \'{current_id}\' WHERE product_id = \'{select_product_id}\'")
            cur.execute(f"DELETE FROM market WHERE product_id = \'{select_product_id}\'")
            print("상품을 구매하였습니다.")
            con.commit()
        else:
            print("상품 구매를 취소합니다.")
    else:
        print("상품이 존재하지 않습니다.")
    print_boundary()

def print_inspector_list(cur):
    sql_query = f"""
                        SELECT id, name, e_mail, introduce
                        FROM inspector;
                    """
    cur.execute(sql_query)
    result = cur.fetchall()
    print("점검자 리스트")
    print(f"|{'점검자 ID'.center(15)}|{'이름'.center(15)}|{'E-Mail'.center(15)}|{'소개'.center(15)}|")
    for record in result:
        print(f"|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{record[3].center(15)}|")

def user_request_inspection(cur):
    print_inspector_list(cur)
    print("점검요청")
    request_product = input("상품 ID: ")
    request_inspector_id = input("점검자 ID: ")
    request_message = input("요청 사항: ")

    cur.execute(f"select * from product where product_id = \'{request_product}\' AND phase_owner = \'{current_id}\' AND certification = False")
    result = cur.fetchall()
    if len(result) == 0:
        print("본인이 구매한 제품, 인증이 안된 제품만 의뢰가능합니다.")
        return

    cur.execute(f"select * from inspector where id = \'{request_inspector_id}\'")
    result = cur.fetchall()
    if len(result) == 0:
        print("없는 점검자 입니다.")
        return

    cur.execute(f"insert into request(request_product_id, client_id, inspector_id, request_message) values (\'{request_product}\',\'{current_id}\',\'{request_inspector_id}\',\'{request_message}\')")
    con.commit()
    print("점검 요청 성공")


def print_phase_list(cur):
    print_boundary()
    sql_query = f"""
                            SELECT E.name, P.product_name, P.product_description, P.price, P.category, P.certification, P.product_id
                            FROM Product P  
                            JOIN Enterprise E ON P.enterprise_id = E.ID
                            WHERE P.phase_owner = \'{current_id}\';
                        """
    cur.execute(sql_query)
    result = cur.fetchall()
    
    print("나의 구매 리스트")
    if len(result) > 0:
        print(f"|{'제품 ID'.center(15)}|{'회사명'.center(15)}|{'상품명'.center(15)}|{'상품 설명'.center(15)}|{'가격'.center(15)}|{'카테고리'.center(15)}|{'인증'.center(15)}|")
        for record in result:
            print(f"|{record[6].center(15)}|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{str(record[3]).center(15)}|{record[4].center(15)}|{str(record[5]).center(15)}|")
    else:
        print("비어있음")

    print_boundary()

def print_request_list(cur):
    print_boundary()
    sql_query = f"""
                        SELECT request_product_id, inspector_id, request_message, request_complete
                        FROM request  
                        WHERE client_id = \'{current_id}\';
                    """
    cur.execute(sql_query)
    result = cur.fetchall()

    print("나의 점검 현황")
    if len(result) > 0:
        print(f"|{'제품 ID'.center(15)}|{'점검자 ID'.center(15)}|{'점검 요청사항'.center(15)}|{'완료 여부'.center(15)}|")
        for record in result:
            print(f"|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{str(record[3]).center(15)}|")
    else:
        print("비어있음")

    print_boundary()

def user_action():
    while True:
        print_user_menu()
        input_select = int(input("Select: "))
        cur = con.cursor()
        if input_select == 1:       # 시장 조회 Todo: 정렬방식 선택?
            print_market(cur)
        elif input_select == 2:     # 물품구매
            buy_product(cur)
        elif input_select == 3:     # 점검요청
            user_request_inspection(cur)
        elif input_select == 4:     # 구매 현황 조회
            print_phase_list(cur)
        elif input_select == 5:
            print_request_list(cur)
        elif input_select == 6:     # 계정 설정
            if not account_setting(cur):     # 계정 삭제됐다면
                break
        elif input_select == 7:     # 로그아웃
            print_logout()
            break
        else:
            print_error_input()

def print_my_product(cur):
    print_boundary()
    sql_query = f"""
                    SELECT E.name, P.product_name, P.product_description, P.price, P.category, P.certification, P.product_id, P.phase_owner
                    FROM Product P  
                    JOIN Enterprise E ON P.enterprise_id = E.ID
                    WHERE E.id = \'{current_id}\';
                """
    cur.execute(sql_query)
    result = cur.fetchall()

    print("기업 판매 리스트")
    if len(result) > 0:
        print(f"|{'제품 ID'.center(15)}|{'회사명'.center(15)}|{'상품명'.center(15)}|{'상품 설명'.center(15)}|{'가격'.center(15)}|{'카테고리'.center(15)}|{'인증'.center(15)}|{'판매여부'.center(15)}|")
        for record in result:
            print(f"|{record[6].center(15)}|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|{str(record[3]).center(15)}|{record[4].center(15)}|{str(record[5]).center(15)}|", end="")
            if str(record[7]) == "None":
                print("False".center(15)+"|")
            else:
                print("True".center(15)+"|")
    else:
        print("비어있음")
    print_boundary()

def enterprise_request_inspection(cur):
    print_boundary()
    print_inspector_list(cur)
    print("점검요청")
    request_product = input("상품 ID: ")
    request_inspector_id = input("점검자 ID: ")
    request_message = input("요청 사항: ")

    cur.execute(f"select * from product where product_id = \'{request_product}\' AND enterprise_id = \'{current_id}\' AND certification = False")
    result = cur.fetchall()
    if len(result) == 0:
        print("자사 제품, 인증이 안된 제품만 의뢰가능합니다.")
        return

    cur.execute(f"select * from inspector where id = \'{request_inspector_id}\'")
    result = cur.fetchall()
    if len(result) == 0:
        print("없는 점검자 입니다.")
        return

    cur.execute(f"insert into request(request_product_id, client_id, inspector_id, request_message) values (\'{request_product}\',\'{current_id}\',\'{request_inspector_id}\',\'{request_message}\')")
    con.commit()
    print("점검 요청 성공")
    print_boundary()

def enterprise_action():
    while True:
        print_enterprise_menu()
        input_select = int(input("Select: "))
        cur = con.cursor()
        if input_select == 1:       # 시장 조회
            print_market(cur)
        elif input_select == 2:   # 판매 물품 등록
            register_product(cur)
        elif input_select == 3:   # 판매 현황 조회
            print_my_product(cur)
        elif input_select == 4:   # 검점요청
            enterprise_request_inspection(cur)
        elif input_select == 5:   # 점검 현황 조회
            print_request_list(cur)
        elif input_select == 6:     # 계정 설정
            if not account_setting(cur):
                break
        elif input_select == 7:     # 로그아웃
            print_logout()
            break
        else:
            print_error_input()

def request_list(cur):
    print_boundary()
    print("----- 미완료 요청 -----")
    cur.execute(f"select request_product_id, client_id, request_message from request where inspector_id = \'{current_id}\' AND request_complete = False")
    result = cur.fetchall()
    print(f"|{'제품 ID'.center(15)}|{'고객 ID'.center(15)}|{'요청 사항'.center(15)}|")
    for record in result:
        print(f"|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|")
    print("----- 완료 요청 -----")
    cur.execute(f"select request_product_id, client_id, request_message from request where inspector_id = \'{current_id}\' AND request_complete = True")
    result = cur.fetchall()
    print(f"|{'제품 ID'.center(15)}|{'고객 ID'.center(15)}|{'요청 사항'.center(15)}|")
    for record in result:
        print(f"|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|")
    print_boundary()

def complete_request(cur):
    print_boundary()
    print("----- 미완료 요청 -----")
    cur.execute(f"select request_product_id, client_id, request_message from request where inspector_id = \'{current_id}\' AND request_complete = False")
    result = cur.fetchall()
    print(f"|{'제품 ID'.center(15)}|{'고객 ID'.center(15)}|{'요청 사항'.center(15)}|")
    for record in result:
        print(f"|{record[0].center(15)}|{record[1].center(15)}|{record[2].center(15)}|")

    select_product_id = input("완료할 상품 ID: ")
    select_certification = input("인증 가능 유무(Y/N): ")
    if select_certification == 'Y':
        cur.execute(f"UPDATE product SET certification = True WHERE product_id = \'{select_product_id}\'")
    elif select_certification == 'N':
        cur.execute(f"UPDATE product SET certification = False WHERE product_id = \'{select_product_id}\'")
    else:
        print_error_input()
        return
    cur.execute(f"UPDATE request SET request_complete = True WHERE request_product_id = \'{select_product_id}\'")
    con.commit()
    print("점검을 완료했습니다.")

    print_boundary()

def change_introduce(cur):
    print_boundary()
    new_introduce = input("변경할 소개 내용을 입력해주세요.\n입력: ")
    cur.execute(f"UPDATE inspector SET introduce = \'{new_introduce}\' WHERE id = \'{current_id}\'")
    con.commit()
    print("소개가 변경되었습니다.")
    print_boundary()

def inspector_action():
    while True:
        print_inspector_menu()
        input_select = int(input("Select: "))
        cur = con.cursor()

        if input_select == 1:       # 시장 조회
            print_market(cur)
        elif input_select == 2:   # 요청된 점검 리스트
            request_list(cur)
        elif input_select == 3:   # 점검 완료 처리
            complete_request(cur)
        elif input_select == 4:   # 소개 변경
            change_introduce(cur)
        elif input_select == 5:  # 계정 설정
            if not account_setting(cur):
                break
        elif input_select == 6:  # 로그아웃
            print_logout()
            break
        else:
            print_error_input()

if __name__ == '__main__':

    while True:
        con = psycopg2.connect(
            database='sample2023',
            user='db2023',
            password='db!2023',
            host='::1',
            port='5432'
        )
        if not enter():
            break

        if current_role == "user":
            user_action()
        elif current_role == "enterprise":
            enterprise_action()
        elif current_role == "inspector":
            inspector_action()
        con.close()
