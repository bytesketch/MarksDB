from sys import (
    argv,
    exit
)

from flask import (
    request,
    Flask,
    jsonify,
    render_template
)

from mysql.connector import (
    connect as sql_connection,
    Error as SQLError
)

import ast

"""
=== BASE MYSQL-WRAPPER CLASS ===

    This class is used for base mysql wrapper and can be used with 'with'
statement of python. This is useful for multiple time connection open. And
with auto close type, this is safe for memory too, but it does not handle
error so that we can control later.

"""
class _Connection:
    def __init__(self, data: dict[str, object]) -> None:
        self.connection = sql_connection(
            host=data["host"],
            user=data["username"],
            password=data["password"],
            database=data["database"]
        )
        self.cursor = self.connection.cursor()
    
    def execute(self, query: str, params: tuple[object, ...] = ()) -> None:
        self.cursor.execute(query, params)
        if not query.strip().upper().startswith("SELECT"):
            self.connection.commit()
    
    def fetchall(self) -> list[tuple[object, ...]]:
        return self.cursor.fetchall()
    
    def fetchone(self) -> tuple[object, ...] | None:
        return self.cursor.fetchone()
    
    def close(self) -> None:
        self.cursor.close()
        self.connection.close()
    
    def __enter__(self) -> _Connection:
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.connection.rollback()
        self.close()

"""
=== _Connection-WRAPPER CLASS ===

    This class is used for ease of connection open and close the _Connection class
with just two lines ::
    db = Conn()
    with db.open() as conn:
        ...

"""
class Conn:
    def __init__(self):
        with open(".cache/mysql.user-model.json") as f:
            self.login = ast.literal_eval(f.read())["login"]
        
    def open(self):
        return _Connection(self.login)

db = Conn()


"""
=== Helper success and error methods ===

    These methods are used to make error and success response easily and
this also helps to standerize the api-call Response.

"""
def error(msg="An unknown error occured at backend."):
    return {
        "status": "error",
        "message": msg
    }

def success(msg, data=None, warning="No warnings."):
    return {
        "status": "success",
        "message": msg,
        "data": data if data else {},
        "warning": warning
    }


"""
=== SQL Injection ===

    This is used to run all initializier scripts into SQL automatically
when server starts.

"""
with open(".cache/mysql.user-model.json") as f:
    raw_data = ast.literal_eval(f.read())["commands"]
with db.open() as conn:
    for command in raw_data:
        conn.execute(command)


app: Flask = Flask(__name__)

"""
=== Server logic : API ===

    These are the total APIs available in the server. These include
 1. Addition of student
 2. Get student's info
 3. Get all students' info
 4. Modify student's info
 5. Delete student
 6. Get all subjects
 7. Get all timings
 8. Add mark record
 9. Get all mark records
10. Get marks for specific student
11. Edit mark record
12. Delete mark record
13. Get develepor information

"""
@app.route("/api/school/info")
@app.route("/api/school/info/")
def get_school_info():
    try:
        print("OK...")
        with open(".cache/mysql.user-model.json") as f:
            data = ast.literal_eval(f.read())
        return jsonify(success("Fetch successful.", data=data["info"])), 200
    except Exception as e:
        return jsonify(error(f"School info file not found. {e}")), 500


@app.route("/api/students/add/", methods=["POST"])
@app.route("/api/students/add", methods=["POST"])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify(error("No JSON data received.")), 400

    try:
        for key in data.keys():
            if key not in ("srno", "name", "class", "roll"):
                return jsonify(error(f"Invalid keyword '{key}'.")), 400

        srno = int(data["srno"])
        name = data["name"]
        clazz = int(data["class"])
        roll = int(data["roll"])

        query = "INSERT INTO student VALUES (%s, %s, %s, %s);"
        with db.open() as conn:
            conn.execute(query, (srno, name, clazz, roll))

        return jsonify(success(f"Student {name} added successfully.")), 201
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except ValueError:
        return jsonify(error("Field 'srno', 'class' and 'roll' should be integer value.")), 400
    except KeyError as e:
        return jsonify(error(f"Missing parameter {e}")), 400
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/student/<int:srno>/get")
@app.route("/api/student/<int:srno>/get/")
def get_student(srno):
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM student WHERE srno=%s;", (srno,))
            raw_data = conn.fetchall()
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 404
        row = raw_data[0]
        if len(row) != 4:
            return jsonify(error("The data is corrupted or mismatched.")), 500
        name = row[1]
        clazz = row[2]
        roll = row[3]
        data = {
            "srno": srno,
            "name": name,
            "class": clazz,
            "roll": roll
        }
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/student/get")
@app.route("/api/student/get/")
def get_all_student():
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM student;")
            raw_data = conn.fetchall()
        
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 404
        
        data = {}
        for row in raw_data:
            name = row[1]
            clazz = row[2]
            roll = row[3]
            data[str(row[0])] = {
                "name": name,
                "class": clazz,
                "roll": roll
            }
        
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/student/<int:srno>/modify", methods=["POST"])
@app.route("/api/student/<int:srno>/modify/", methods=["POST"])
def modify_student(srno):
    data = request.get_json()
    if not data:
        return jsonify(error("No JSON data received.")), 400
    
    try:
        keys = data.keys()
        for key in keys:
            if key not in ("name", "class", "roll"):
                return jsonify(error(f"Invalid keyword '{key}'.")), 400
        
        result = {}
        changes = 0
        with db.open() as conn:
            if "name" in keys:
                conn.execute("UPDATE student SET name=%s WHERE srno=%s;", (data["name"], srno))
                result[str(changes)] = "Changed name."
                changes += 1
            if "class" in keys:
                conn.execute("UPDATE student SET class=%s WHERE srno=%s;", (int(data["class"]), srno))
                result[str(changes)] = "Changed class."
                changes += 1
            if "roll" in keys:
                conn.execute("UPDATE student SET roll_no=%s WHERE srno=%s;", (int(data["roll"]), srno))
                result[str(changes)] = "Changed roll."
                changes += 1
        result["changes"] = changes

        return jsonify(success("Change query was succesfull.", data=result, warning=
                               "No warnings." if changes > 0 else "No changes occurred.")), 201
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except ValueError:
        return jsonify(error("Field 'class' and 'roll' should be integer value.")), 400
    except KeyError as e:
        return jsonify(error(f"Missing parameter {e}")), 400
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/student/<int:srno>/del", methods=["POST"])
@app.route("/api/student/<int:srno>/del/", methods=["POST"])
def del_student(srno):
    try:
        with db.open() as conn:
            conn.execute("DELETE FROM student WHERE srno=%s;", (srno,))

        return jsonify(success("Student delete success."))
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/subjects")
@app.route("/api/subjects/")
def get_all_subjects():
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM subjects;")
            raw_data = conn.fetchall()
        
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 200
        
        data = {}
        for row in raw_data:
            data[str(row[0])] = row[1]
        
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/timing")
@app.route("/api/timing/")
def get_all_timing():
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM timing;")
            raw_data = conn.fetchall()
        
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 200
        
        data = {}
        for row in raw_data:
            data[str(row[0])] = row[1]
        
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/marks/<int:srno>/add", methods=["POST"])
@app.route("/api/marks/<int:srno>/add/", methods=["POST"])
def add_mark_record(srno):
    data = request.get_json()
    if not data:
        return jsonify(error("No JSON data received.")), 400

    try:
        keys = data.keys()
        for key in keys:
            if key not in ("subject", "timing", "max", "obtained"):
                return jsonify(error(f"Invalid keyword '{key}'.")), 400
        
        subject = int(data["subject"])
        timing = int(data["timing"])
        max_marks = int(data["max"])
        obtained = float(data["obtained"])

        if obtained > max_marks:
            return jsonify(error("Obtained marks should always be less or equal than max marks.")), 400

        query = ("INSERT INTO marks (stu_id, sub_id, tim_id, max_marks, marks) "
                 "VALUES (%s, %s, %s, %s, %s);")
        with db.open() as conn:
            conn.execute(query, (srno, subject, timing, max_marks, obtained))
        return jsonify(success("Marks added successful.")), 201
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except ValueError:
        return jsonify(error("Field 'subject', 'timing' and 'max' should be integer value "
                             "and 'obtained' should be decimal value.")), 400
    except KeyError as e:
        return jsonify(error(f"Missing parameter {e}")), 400
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/marks/get")
@app.route("/api/marks/get/")
def get_all_marks_records():
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM marks;")
            raw_data = conn.fetchall()
        
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 200
        
        data = {}
        for row in raw_data:
            data[str(row[0])] = {
                "student": row[1],
                "subject": row[2],
                "timing": row[3],
                "max_marks": row[4],
                "marks": row[5]
            }
        
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/marks/<int:uid>/get")
@app.route("/api/marks/<int:uid>/get/")
def get_marks_records(uid):
    try:
        with db.open() as conn:
            conn.execute("SELECT * FROM marks WHERE stu_id=%s;", (uid,))
            raw_data = conn.fetchall()
        
        if not raw_data:
            return jsonify(success("Fetch was successful.", warning="No record found.")), 200
        
        data = {}
        for row in raw_data:
            data[str(row[0])] = {
                "subject": row[2],
                "timing": row[3],
                "max_marks": row[4],
                "marks": row[5]
            }
        
        return jsonify(success("Fetch was successful.", data=data)), 200
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/marks/<int:recid>/update", methods=["POST"])
@app.route("/api/marks/<int:recid>/update/", methods=["POST"])
def update_mark_record(recid):
    data = request.get_json()
    if not data:
        return jsonify(error("No JSON data received.")), 400
    
    try:
        keys = data.keys()
        for key in keys:
            if key not in ("subject", "timing", "max", "obtained"):
                return jsonify(error(f"Invalid keyword '{key}'.")), 400
        
        marks_to_update = "obtained" in keys
        max_to_updated = "max" in keys
        subject_to_updated = "subject" in keys
        timing_to_update = "timing" in keys
        
        updated = []
        with db.open() as conn:
            conn.execute("SELECT max_marks FROM marks WHERE id=%s;", (recid,))
            raw = conn.fetchall()
            if not raw:
                return jsonify(error("Record not found.")), 404
            max_marks = raw[0][0]
            conn.execute("SELECT marks FROM marks WHERE id=%s;", (recid,))
            raw = conn.fetchall()
            if not raw:
                return jsonify(error("Record not found.")), 404
            marks = raw[0][0]

            if max_to_updated:
                max_marks = int(data["max"])
                updated.append("max")

            if marks_to_update:
                marks = float(data["obtained"])
                if marks > max_marks:
                    return jsonify(error("Marks cannot be greater than max marks."))
                updated.append("obtained")
            conn.execute("UPDATE marks SET marks=%s, max_marks=%s WHERE id=%s;", (marks, max_marks, recid))

            if subject_to_updated:
                subject = int(data["subject"])
                conn.execute("UPDATE marks SET sub_id=%s WHERE id=%s;", (subject, recid))
                updated.append("subject")
            
            if timing_to_update:
                timing = int(data["timing"])
                conn.execute("UPDATE marks SET tim_id=%s WHERE id=%s;", (timing, recid))
                updated.append("timing")
        return jsonify(success(f"Updated {', '.join(updated)}."))           
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except ValueError:
        return jsonify(error("Field 'subject', 'timing' and 'max' should be integer value "
                             "and 'obtained' should be decimal value.")), 400
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/marks/<int:recid>/del", methods=["POST"])
@app.route("/api/marks/<int:recid>/del/", methods=["POST"])
def del_mark_record(recid):
    try:
        with db.open() as conn:
            conn.execute("DELETE FROM marks WHERE id=%s;", (recid,))

        return jsonify(success("Mark record delete success."))
    except SQLError as e:
        return jsonify(error(f"SQL Error occured: {e}")), 500
    except Exception as e:
        print(e)
        return jsonify(error()), 500

@app.route("/api/developer")
@app.route("/api/developer/")
def get_dev():
    return jsonify(success("Fetch successful.", data={
        "name": "Ali Ahmad",
        "github": "bytesketch"
    })), 200

"""
=== Main page ===
    The main entry page of the website. The page is available as
1. "http(s)://..."
2. "http(s)://.../"
3. "http(s)://.../home"
4. "http(s)://.../home/"
5. "http(s)://.../index.html"

"""
@app.route("/")
@app.route("/index.html")
@app.route("/home")
@app.route("/home/")
def home():
    return render_template("index.html")


"""
=== The entry point ===
    This is the starting part of server. To run the server, the following
commands are applicable:
1. python3 server.py [port:int=8080]
    :: NOTE  : You will need to pass an integer value to start server at that
               port. Default=8080
    :: NOTE-2: You will need to have `mysql-connector-python` and `flask` to be
               installed in your environment.
2. ./app --start server [port:int=8080]
    :: NOTE : You will need to have a full setup (Run `./app --configure <mysql-username>`)
    :: The `app`     script is provided for Linux/macOS.
    :: The `app.bat` script if provided for Windows.

    :: To stop server, run `./app --stop-server [port:int=8080]`
    ::    :: NOTE : This will kill any process on port=localhost:port.

"""
if __name__ == "__main__":
    port: int = 8080
    try:
        port = int(argv[1])
    except ValueError:
        print("The port number should be a integer value.")
        exit (400)
    except IndexError:
        port = 8080

    print(f"Running at port {port}.")
    app.run(port=port)
    exit   (0)
