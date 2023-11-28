import psycopg2

con = psycopg2.connect(
    database = 'sample2023',
    user = 'db2023',
    password = 'db!2023',
    host = '::1',
    port = '5432'
)

current_name, current_role = None, None

def print_boundary():
    print("-" * 30)
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
            cur.execute(f"SELECT name FROM {current_role} WHERE ID = %s", (input_id,))
            result = cur.fetchone()
            current_name = result[0]
            print("로그인 성공! Hi,", current_name, sep=" ")
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

def register_user(cursor, input_id, input_password, input_nickname, email, role, inspector_introduce=None):
    if role == 1:  # User
        cursor.execute("INSERT INTO \"User\" (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "User"))
    elif role == 2:  # Enterprise
        cursor.execute("INSERT INTO Enterprise (ID, name, e_mail) VALUES (%s, %s, %s)", (input_id, input_nickname, email))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "Enterprise"))
    elif role == 3:  # Inspector
        cursor.execute("INSERT INTO Inspector (ID, name, e_mail, introduce) VALUES (%s, %s, %s, %s)",
                       (input_id, input_nickname, email, inspector_introduce))
        cursor.execute("INSERT INTO Register (ID, password, role) VALUES (%s, %s, %s)", (input_id, input_password, "Inspector"))

    # register 테이블에 ID와 Password 등록


def register():
    global con
    cur = con.cursor()

    print_boundary()
    print("Please fill out your registration information!")
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

if __name__ == '__main__':

    while True:
        if not enter():
            break

        # if current_role == "User":
        #
        # elif current_role == "Enterprise":
        #
        # elif current_role == "Inspector":

    con.close()
