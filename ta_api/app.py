import sqlite3
from flask import Flask, request, jsonify

def connect_to_db():
    conn = sqlite3.connect('db_akademik.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
        CREATE TABLE IF NOT EXISTS tbl_users (
            user_id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        );
        ''')
        conn.commit()
        print('Tabel user berhasil dibuat')
    except:
        print('Tabel user gagal dibuat')
    finally:
        conn.close()
    
def insert_user(user):
        inserted_user = {}
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO tbl_users(name, email, address) VALUES (?, ?, ?)", (user['name'], user['email'], user['address']))
            conn.commit()
            #inserted_user = user

        except Exception as e:
            print(f"Error: {e}")
            conn().rollback()
        finally:
            conn.close()
        return inserted_user

def get_users():
    users = []
    
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_users")
        rows = cur.fetchall()
        
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["name"] = i["name"]
            user["email"] = i["email"]
            user["address"] = i["address"]
            users.append(user)
    except:
        users = []
    return users

def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbl_users WHERE user_id = ?", (user_id))
        row = cur.fetchone()
        
        if row is not None:
            user["user_id"] = row["user_id"]
            user["name"] = row["name"]
            user["email"] = row["email"]
            user["address"] = row["address"]
    except Exception as e:
        print(f"Error: {e}")
    return user

def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE tbl_users SET name = ?, email = ?, address = ? WHERE user_id = ?",
                    (user["name"], user["email"], user["address"], user["user_id"],))
        conn.commit
        updated_user = get_user_by_id(user["user_id"])
    except:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()
    return updated_user

def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM tbl_users WHERE user_id = ?", (user_id))
        conn.commit()
        message["status"] = "User deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()
    return message

users = []
'''
user0 = {
    "name": "Budi",
    "email": "budi@gmail.com",
    "address": "Jogja"
}
user1 = {
    "name": "Andi",
    "email": "andi@gmail.com",
    "address": "Sleman"
}

users.append(user0)
users.append(user1)
'''
create_db_table()
'''
for i in users:
    print(insert_user(i))
'''
app = Flask(__name__)

@app.route('/users', methods=['GET'])
def api_get_users():
    users = get_users()
    if users:
        return jsonify(users), 200  # Sukses dengan kode status 200
    else:
        return jsonify({'message': 'No users found.'}), 404

@app.route('/users/<user_id>', methods=['GET'])
def api_get_users_by_id(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route('/users', methods=['POST'])
def api_add_users():
    user = request.get_json()
    return jsonify(insert_user(user))

@app.route('/users', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))

@app.route('/users/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))

if __name__ == "__main__":
    app.run(debug=True, port=4444)
