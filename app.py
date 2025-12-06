import jwt
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import mysql.connector

# import pymysql

# import jwt

app = Flask(__name__)

conn = mysql.connector.connect(
    user='root',
    host='localhost',
    password='Sandeep@05',
    database='flask_tutorial'
)
print("connected")


@app.route('/')
def home():
    return 'Welcome to Flask Service'


@app.route('/getTable', methods=['GET'])
def get_table():
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
    table_names = [table[0] for table in tables]
    return jsonify({"tables": table_names}), 200


@app.route('/addUsers', methods=['POST'])
def add_users():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    password = data.get('password')
    cursor = conn.cursor()
    sql_query = "INSERT INTO users (name,email,phone,role,password) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(sql_query, (name, email, phone, role, password))
    conn.commit()
    return jsonify({"message": "Data inserted successfully!!"}), 201


@app.route('/fetchAllUsers', methods=['GET'])
def get_all_student():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) > 0:
        return jsonify({
            'data': rows})
    else:
        return jsonify({'message': 'Data not Found'})


@app.route('/fetchUserById/<string:phone>', methods=['GET'])
def fetch_user_by_id(phone):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE phone=%s", (phone,))
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route('/updateUserDetails', methods=['PUT'])
def update_user_details():
    id = request.json.get('id')
    name = request.json.get('name')
    return jsonify({"message": "this is update user details api"})


@app.route('/upadteStudentDetailS', methods=['PUT'])
def update_data():
    id = request.json.get('id')
    name = request.json.get('name')
    mark = request.json.get('mark')
    cursor = conn.cursor()
    query = "UPDATE student SET name=%s,mark=%s WHERE id=%s"
    cursor.execute(query, (name, mark, id))
    conn.commit()
    cursor.close()
    if cursor.rowcount > 0:
        return jsonify({"message": "Updated record successfully!!"}), 201
    else:
        return jsonify({"message": "Nothing to Update"}), 202


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_data(id):
    cursor = conn.cursor()
    query = "DELETE FROM student where id=%s"
    cursor.execute(query, (id,))
    conn.commit()
    cursor.close()
    if cursor.rowcount > 0:
        return jsonify({"message": "deleted record successfully !!"}), 200
    else:
        return jsonify({"message": "Nothing to Delete"}), 204


@app.route('/patchUpdate/<int:id>', methods=['PATCH'])
def patch_data(id):
    qry = "UPDATE student SET "
    data = request.form
    for key in data:
        qry += f"{key}={data[key]},"
    qry = qry[:-1] + f" WHERE id={id}"

    cursor = conn.cursor()
    cursor.execute(qry)
    conn.commit()
    cursor.close()
    print(qry)
    if cursor.rowcount > 0:
        return jsonify({"message": "Data updated successfully"}), 201
    else:
        return jsonify({'message': "Nothing to update"}), 202


@app.route('/login', methods=['POST'])
def user_login():
    cursor = conn.cursor()
    data = request.form
    qry = f"SELECT id, name, email, phone, role_id FROM user WHERE email='{data['username']}' and password='{data['password']}'"
    cursor.execute(qry)
    result = cursor.fetchall()
    userdata = result[0]
    exp_time = datetime.now() + timedelta(minutes=15)
    exp_epoch_time = int(exp_time.timestamp())
    payload = {
        "payload": userdata,
        "exp": exp_epoch_time
    }

    jwtoken = jwt.encode(payload, "sandeep", algorithm="HS256")
    return jsonify({"token": jwtoken}), 200


if __name__ == "__main__":
    print("connecting to DB...")
    app.debug = True
    app.run(host='0.0.0.0', debug=True)
