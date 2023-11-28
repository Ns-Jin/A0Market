import psycopg2

con = None
current_name, current_role = None, None

def print_boundary():
    print("-" * 20)
def login():
    global con
    global current_name
    global current_role

    input_id = input("ID: ")
    input_password = input("Password: ")

    cur = con.cursor()

    try:
        # 입력 받은 ID와 Password를 사용하여 쿼리 실행
        cur.execute("SELECT role FROM Register WHERE ID = %s AND password = %s", (input_id, input_password))

        # 결과 가져오기
        result = cur.fetchone()

        if result:
            current_role = result[0]
            cur.execute(f"SELECT name FROM \"{current_role}\" WHERE ID = %s", (input_id,))
            result = cur.fetchone()
            current_name = result[0]
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
    create_user(input_id, input_password)
    # Todo: DB user를 등록하고 해당 user의 권한을 부여하기 위해 role을 만들고 해당 role을 부여
    if role == 1:  # User
        cursor.execute("INSERT INTO \"User\" (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "user"))
        cursor.execute(f"GRANT SELECT, INSERT ON TABLE market, product, enterprise, inspector TO {input_id}")
        cursor.execute(f"GRANT ALL ON TABLE wish, \"User\", request TO {input_id}")
        cursor.execute(f"GRANT DELETE, UPDATE ON TABLE register TO {input_id}")
    elif role == 2:  # Enterprise
        cursor.execute("INSERT INTO Enterprise (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "enterprise"))
        cursor.execute(f"GRANT SELECT, INSERT ON TABLE market, product, \"User\", inspector TO {input_id}")
        cursor.execute(f"GRANT ALL ON TABLE wish, enterprise, request TO {input_id}")
        cursor.execute(f"GRANT DELETE, UPDATE ON TABLE register TO {input_id}")
    elif role == 3:  # Inspector
        cursor.execute("INSERT INTO Inspector (ID, name, e_mail, introduce) VALUES (%s, %s, %s, %s)",
                       (input_id, input_nickname, email, inspector_introduce))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "inspector"))
        cursor.execute(f"GRANT SELECT, INSERT ON TABLE market, product, enterprise, \"User\" TO {input_id}")
        cursor.execute(f"GRANT ALL ON TABLE wish, inspector, request TO {input_id}")
        cursor.execute(f"GRANT DELETE, UPDATE ON TABLE register TO {input_id}")

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
    print("Todo: Manage Database")
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
    print("2. 구매 현황 조회")
    print("3. 계정 설정")
    print("4. 로그아웃")
    print_boundary()

def print_enterprise_menu():
    print_boundary()
    print("1. 시장 조회")
    print("2. 판매 물품 등록")
    print("3. 판매 현황 조회")
    print("4. 검점자와 interaction")
    print("5. 정산")
    print("6. 계정 설정")
    print("7. 로그아웃")
    print_boundary()
def print_inspector_menu():
    print_boundary()
    print("1. 시장 조회")
    print("2. 정산")
    print("3. 계정 설정")
    print("4. 로그아웃")
    print_boundary()

def print_error_input():
    print("잘못된 입력입니다.")

def print_logout():
    print("로그아웃 하였습니다.")

def user_action():
    while True:
        print_user_menu()
        input_select = int(input("Select: "))
        if input_select == 1:       # 시장 조회
            cur = con.cursor()
            # SQL 쿼리 작성
            sql_query = """
                SELECT E.name, P.product_name, P.product_description, P.price, M.enrollment_date, P.category, P.certification
                FROM Product P
                JOIN Market M ON P.product_id = M.product_id
                JOIN Enterprise E ON P.enterpriseID = E.ID;
            """
            # 쿼리 실행
            cur.execute(sql_query)
            # 결과 가져오기
            result = cur.fetchall()
            print(result)
        # elif input_select == 2:     # 구매 현황 조회
        # elif input_select == 3:     # 계정 설정
        # elif input_select == 4:     # 로그아웃
        #     print_logout()
        #     break
        else:
            print_error_input()


def enterprise_action():
    while True:
        print_enterprise_menu()
        input_select = int(input("Select: "))
def inspector_action():
    while True:
        print_inspector_menu()
        input_select = int(input("Select: "))

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

        if current_role == "User":
            user_action()
        elif current_role == "Enterprise":
            enterprise_action()
        elif current_role == "Inspector":
            inspector_action()
        con.close()
