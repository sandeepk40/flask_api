import jwt
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import mysql.connector
import json
from datetime import datetime

app = Flask(__name__)

conn = mysql.connector.connect(
    host="mysql.railway.internal",
    user="root",
    password="vpjsTiqqxfFfgNcdMptAHZjPcVpogJDT",
    database="railway"
)
print("Connected successfully to MySQL on Railway!")


# conn = mysql.connector.connect(
#     user='root',
#     host='localhost',
#     password='Sandeep@05',
#     database='flask_tutorial'
# )
# print("connected")


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
    flatNo = data.get('flatNo')
    phone = data.get('phone')
    role = data.get('role')
    buildingName = data.get('buildingName')
    landmark = data.get('landmark')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location = data.get('location')
    fcmtoken = data.get('fcmtoken')

    # 🔥 Server DateTime
    server_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    createdDate = server_datetime
    # updatedDate = server_datetime

    # 🔥 Convert list of objects → JSON string
    inprogressOrder = json.dumps(data.get('inprogressOrder', []))
    completedOrder = json.dumps(data.get('completedOrder', []))

    cursor = conn.cursor()

    sql_query = """
    INSERT INTO users 
    (name, flatNo, phone, role, buildingName, landmark, latitude, longitude,
     location, fcmtoken, createdDate, inprogressOrder, completedOrder)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql_query, (
        name, flatNo, phone, role, buildingName, landmark, latitude, longitude,
        location, fcmtoken, createdDate,
        inprogressOrder, completedOrder
    ))

    conn.commit()

    return jsonify({"message": "Data inserted successfully!!"}), 201


@app.route('/updateOrderStatus', methods=['POST'])
def update_order_status():
    data = request.get_json()

    userId = data.get('userId')
    orderType = data.get('orderType')  # "inprogressOrder" or "completedOrder"
    orderId = data.get('orderId')
    newStatus = data.get('newStatus')

    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Fetch existing JSON array
    cursor.execute(f"SELECT {orderType} FROM users WHERE id = %s", (userId,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "User not found"}), 404

    # 2️⃣ Convert JSON string → Python list
    order_list = json.loads(row[orderType])

    # 3️⃣ Update status for matching orderId
    for order in order_list:
        if order["id"] == orderId:
            order["status"] = newStatus

    # 4️⃣ Convert list → JSON string
    updated_orders_json = json.dumps(order_list)

    # 5️⃣ Update DB
    cursor.execute(
        f"UPDATE users SET {orderType} = %s WHERE id = %s",
        (updated_orders_json, userId)
    )
    conn.commit()

    return jsonify({"message": "Order status updated successfully!"})


@app.route('/updateFcmToken/<int:userId>', methods=['PUT'])
def update_fcm_token(userId):
    data = request.get_json()

    fcmtoken = data.get('fcmtoken')

    if not fcmtoken:
        return jsonify({"error": "fcmtoken is required"}), 400

    cursor = conn.cursor()

    # 🔥 Update updatedDate with server time
    server_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = """
        UPDATE users 
        SET fcmtoken = %s, updatedDate = %s
        WHERE id = %s
    """

    cursor.execute(sql, (fcmtoken, server_datetime, userId))
    conn.commit()

    return jsonify({"message": "FCM token updated successfully!"}), 200


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


@app.route('/updateStudentDetails', methods=['PUT'])
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
