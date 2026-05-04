from typer import prompt
from sys import exit
from json import dump as jsonify
from click.exceptions import Abort


def main():
    data = {}

    print("=== === === INFO === === ===")

    usrname = prompt(":: Enter username existing or new", default="root")
    pssword = prompt(":: Enter password for/of the user", hide_input=True)
    database = prompt(":: Database").strip()
    host = prompt(":: Enter host name", default="localhost")

    if not database:
        print("Invalid database name.")
        print("Database name cannot be empty.")
        exit(1)
    
    valid = "qwertyuiopasdfghjklzxcvbnm_1234567890"
    if database[0].lower() not in valid[:26]:
        print("Invalid database name.")
        print("First character should be an alphabet.")
        exit(1)

    for c in database.lower():
        if c not in valid:
            print("Invalid database name.")
            print(f"Special character (except underscore) is not allowed.")
            exit(1)
    
    data["login"] = {
        "username": usrname,
        "password": pssword,
        "database": database,
        "host": host
    }

    data["commands"] = [
        "CREATE TABLE IF NOT EXISTS student(srno INT PRIMARY KEY, name VARCHAR(30) NOT NULL, class INT NOT NULL, roll_no INT NOT NULL, CHECK (srno > 0), CHECK (class > 0 AND class <= 12), CHECK (roll_no > 0), UNIQUE (class, roll_no));",
        "CREATE TABLE IF NOT EXISTS subjects (code INT PRIMARY KEY, name VARCHAR(30) NOT NULL, CHECK (code > 0));",
        "CREATE TABLE IF NOT EXISTS timing(code INT PRIMARY KEY, name VARCHAR(30) NOT NULL, CHECK (code > 0));",
        "CREATE TABLE IF NOT EXISTS marks(id INT PRIMARY KEY AUTO_INCREMENT, stu_id INT NOT NULL, sub_id INT NOT NULL, tim_id INT NOT NULL, max_marks INT NOT NULL, marks DECIMAL(5,2) NOT NULL, CHECK (max_marks > 0), CHECK (marks >= 0), UNIQUE (stu_id, sub_id, tim_id), FOREIGN KEY (stu_id) REFERENCES student(srno) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (sub_id) REFERENCES subjects(code) ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY (tim_id) REFERENCES timing(code) ON DELETE RESTRICT ON UPDATE CASCADE);",

        "INSERT INTO subjects (code, name) VALUES (402, 'IT') ON DUPLICATE KEY UPDATE name = VALUES(name);",

        "INSERT INTO timing (code, name) VALUES (1, 'Periodic Test 1') ON DUPLICATE KEY UPDATE name = VALUES(name);",
        "INSERT INTO timing (code, name) VALUES (2, 'Half Yearly') ON DUPLICATE KEY UPDATE name = VALUES(name);",
        "INSERT INTO timing (code, name) VALUES (3, 'Periodic Test 2') ON DUPLICATE KEY UPDATE name = VALUES(name);",
        "INSERT INTO timing (code, name) VALUES (4, 'Final Examination') ON DUPLICATE KEY UPDATE name = VALUES(name);",
        "INSERT INTO timing (code, name) VALUES (5, 'Pre-board 1') ON DUPLICATE KEY UPDATE name = VALUES(name);",
        "INSERT INTO timing (code, name) VALUES (6, 'Pre-board 2') ON DUPLICATE KEY UPDATE name = VALUES(name);"
    ]

    print("=== === === SCHOOL === === ===")

    name = prompt(":: School name")
    addr0 = prompt(":: Area and City")
    addr1 = prompt(":: District")
    addr2 = prompt(":: PIN code")
    addr3 = prompt(":: State")
    addr4 = prompt(":: Country")
    desc = prompt(":: One line description")
    remarks = []

    print("Now add all remarks. Press CTRL+C to stop adding commands.")
    i = 1
    while True:
        try:
            remarks.append(prompt(f"Remark {i}"))
            i += 1
        except Abort, KeyboardInterrupt:
            break
    
    data["info"] = {
        "name": name,
        "address": [addr0, addr1, addr2, addr3, addr4],
        "description": desc,
        "remarks": remarks
    }

    with open(".cache/mysql.user-model.json", "w") as f:
        jsonify(data, f, indent=4, sort_keys=True)
    
    with open(".cache/mysql.user-root.sql", "w") as f:
        f.write(f"""CREATE USER IF NOT EXISTS '{usrname}'@'{host}' IDENTIFIED BY '{pssword}';
CREATE DATABASE IF NOT EXISTS {database};
GRANT ALL PRIVILEGES ON {database}.* TO '{usrname}'@'{host}';
""")
    print("User modal and root inject files were created successfully.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, Abort:
        print("\nCancelling...")
    except Exception as e:
        print(f"\nAn error caught: {e}")
