from flask import Flask, request, jsonify
import pyodbc
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Kết nối tới cơ sở dữ liệu SQL Server
connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-VS9OVGK;Database=GameCrack;Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


@app.route('/api/login', methods=['POST'])
def login():
    try:
        # Lấy thông tin đăng nhập từ yêu cầu POST
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Thực hiện kiểm tra đăng nhập trong cơ sở dữ liệu
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            # Đăng nhập thành công
            return jsonify({"message": "Đăng nhập thành công"})
        else:
            # Đăng nhập không thành công
            return jsonify({"message": "Đăng nhập không thành công"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/api/register', methods=['POST'])
def register():
    try:
        # Lấy thông tin đăng ký từ yêu cầu POST
        data = request.get_json()
        fullname = data.get('fullname')
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        # Kiểm tra xem các trường thông tin đã được gửi
        if not fullname or not username or not password or not email:
            return jsonify({"message": "Vui lòng điền đầy đủ thông tin."}), 400

        # Kiểm tra xem người dùng có tồn tại trong cơ sở dữ liệu không
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "Tên đăng nhập đã tồn tại."}), 409

        # Thêm người dùng mới vào cơ sở dữ liệu
        cursor.execute("INSERT INTO Users (FullName, Username, Password, Email) VALUES (?, ?, ?, ?)",
                       (fullname, username, password, email))
        conn.commit()

        if cursor.rowcount == 1:
            return jsonify({"message": "Đăng ký thành công."}), 201
        else:
            return jsonify({"message": "Không thể thêm người dùng."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users")
        
        # Chuyển đổi kết quả thành danh sách các dictionary
        users = []
        for row in cursor.fetchall():
            user = {
                "UserID": row.UserID,
                "Username": row.Username,
                "Password":row.Password,
                "Email": row.Email,
                "Fullname": row.Fullname,
            }
            users.append(user)
        
        connection.close()
        
        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE UserID=?", (user_id,))
        
        user = cursor.fetchone()
        if user:
            user_data = {
                "UserID": user.UserID,
                "Username": user.Username,
                "Password": user.Password,
                "Email": user.Email,
                "Fullname": user.Fullname,
            }
            connection.close()
            return jsonify(user_data), 200
        else:
            connection.close()
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Users (Username, Password, Email, Fullname) VALUES (?, ?, ?, ?)",
                       (data['Username'], data['Password'], data['Email'], data['Fullname']))
        connection.commit()
        connection.close()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("UPDATE Users SET Username=?, Password=?, Email=?, Fullname=? WHERE UserID=?",
                       (data['Username'], data['Password'], data['Email'], data['Fullname'], user_id))
        connection.commit()
        connection.close()
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Games
@app.route('/api/games', methods=['GET'])
def get_games():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Games")
        
        games = []
        for row in cursor.fetchall():
            game_data = {
                "GameID": row.GameID,
                "GameName": row.GameName,
                "GameTitle": row.GameTitle,
                "Genre": row.Genre,
                "ReleaseDate": row.ReleaseDate.strftime('%Y-%m-%d') if row.ReleaseDate else None,
                "ImageURL": row.ImageURL
            }
            games.append(game_data)
        
        return jsonify(games), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Games_Detail
@app.route('/api/games/<int:game_id>/details', methods=['GET'])
def get_game_details(game_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                G.GameName,
                G.GameTitle,
                G.Genre,
                G.ReleaseDate,
                G.ImageURL AS GameImage,
                GD.Publisher,
                GD.PostDate,
                GD.Description,
                GD.DownloadLink,
                GD.PurchaseLink,
                'Minimum' AS RequirementType,
                SI.Processor AS MinimumProcessor,
                SI.Memory AS MinimumMemory,
                SI.Graphics AS MinimumGraphics,
                SI.Storage AS MinimumStorage,
                SR.Processor AS RecommendedProcessor,
                SR.Memory AS RecommendedMemory,
                SR.Graphics AS RecommendedGraphics,
                SR.Storage AS RecommendedStorage,
                GI.ImageURL AS SystemImage,
                C.CommentID,
                C.UserID AS CommentUserID,
                U.Username AS CommentUsername,
                C.CommentText,
                C.CommentDate
            FROM
                Games AS G
            JOIN
                GameDetails AS GD ON G.GameID = GD.GameID
            LEFT JOIN
                SystemRequirements AS SI ON GD.GameDetailID = SI.GameDetailID
            LEFT JOIN
                SystemRequirements AS SR ON GD.GameDetailID = SR.GameDetailID AND SR.Type = 'Recommended'
            LEFT JOIN
                GameImages AS GI ON GD.GameDetailID = GI.GameDetailID
            LEFT JOIN
                Comments AS C ON GD.GameDetailID = C.GameDetailID
            LEFT JOIN
                Users AS U ON C.UserID = U.UserID
            WHERE G.GameID = ?
        """, (game_id,))
        
        game_detail = cursor.fetchone()
        if game_detail:
            game_data = {
                "GameName": game_detail.GameName,
                "GameTitle": game_detail.GameTitle,
                "Genre": game_detail.Genre,
                "ReleaseDate": game_detail.ReleaseDate.strftime('%Y-%m-%d') if game_detail.ReleaseDate else None,
                "GameImage": game_detail.GameImage,
                "Publisher": game_detail.Publisher,
                "PostDate": game_detail.PostDate.strftime('%Y-%m-%d') if game_detail.PostDate else None,
                "Description": game_detail.Description,
                "DownloadLink": game_detail.DownloadLink,
                "PurchaseLink": game_detail.PurchaseLink,
                "MinimumRequirements": {
                    "RequirementType": "Minimum",
                    "Processor": game_detail.MinimumProcessor,
                    "Memory": game_detail.MinimumMemory,
                    "Graphics": game_detail.MinimumGraphics,
                    "Storage": game_detail.MinimumStorage,
                },
                "RecommendedRequirements": {
                    "RequirementType": "Recommended",
                    "Processor": game_detail.RecommendedProcessor,
                    "Memory": game_detail.RecommendedMemory,
                    "Graphics": game_detail.RecommendedGraphics,
                    "Storage": game_detail.RecommendedStorage,
                },
                "SystemImage": game_detail.SystemImage,
                "CommentID": game_detail.CommentID,
                "CommentUserID": game_detail.CommentUserID,
                "CommentUsername": game_detail.CommentUsername,
                "CommentText": game_detail.CommentText,
                "CommentDate": game_detail.CommentDate.strftime('%Y-%m-%d') if game_detail.CommentDate else None
            }
            return jsonify(game_data), 200
        else:
            return jsonify({"error": "Game not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Game mới
@app.route('/api/games/newest', methods=['GET'])
def get_newest_games():
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 5
                G.GameID,
                G.GameName,
                G.GameTitle,
                G.Genre,
                G.ReleaseDate,
                G.ImageURL AS GameImage
            FROM
                Games AS G
            ORDER BY
                G.ReleaseDate DESC;
        """)
        
        newest_games = []
        for row in cursor.fetchall():
            game_data = {
                "GameID": row.GameID,
                "GameName": row.GameName,
                "GameTitle": row.GameTitle,
                "Genre": row.Genre,
                "ReleaseDate": row.ReleaseDate.strftime('%Y-%m-%d') if row.ReleaseDate else None,
                "GameImage": row.GameImage
            }
            newest_games.append(game_data)
        
        return jsonify(newest_games), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Game update
@app.route('/api/games/latest', methods=['GET'])
def get_latest_game_details():
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                GD.GameDetailID,
                G.ImageURL,
                G.GameName,
                G.GameTitle,
                GD.UpdateDate
            FROM
                GameDetails AS GD
            JOIN
                Games AS G ON GD.GameID = G.GameID
            ORDER BY GD.UpdateDate DESC;
        """)
        
        latest_game_details = []
        for row in cursor.fetchall():
            game_detail_data = {
                "GameDetailID": row.GameDetailID,
                "ImageURL": row.ImageURL,
                "GameName": row.GameName,
                "GameTitle": row.GameTitle,
                "UpdateDate": row.UpdateDate.strftime('%Y-%m-%d') if row.UpdateDate else None
            }
            latest_game_details.append(game_detail_data)
        
        return jsonify(latest_game_details), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Game Hot

@app.route('/api/games/<string:genre>', methods=['GET'])
def get_games_by_genre(genre):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                G.GameName,
                G.GameTitle,
                G.Genre,
                G.ImageURL,
                GD.DownloadCount
            FROM
                Games AS G
            JOIN
                GameDetails AS GD ON G.GameID = GD.GameID
            WHERE
                G.Genre = ?
            ORDER BY
                GD.DownloadCount DESC;
        """, (genre,))
        
        games_by_genre = []
        for row in cursor.fetchall():
            game_data = {
                "GameName": row.GameName,
                "GameTitle": row.GameTitle,
                "Genre": row.Genre,
                "ImageURL": row.ImageURL,
                "DownloadCount": row.DownloadCount
            }
            games_by_genre.append(game_data)
        
        return jsonify(games_by_genre), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system-requirements', methods=['GET'])  
def get_system_requirements():
    try:
        # Thực hiện truy vấn SQL để lấy dữ liệu từ bảng SystemRequirements
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SystemRequirements")
        data = cursor.fetchall()

        # Chuyển kết quả thành danh sách các bản ghi JSON
        requirements_list = []
        for row in data:
            requirement = {
                "RequirementID": row.RequirementID,
                "GameDetailID": row.GameDetailID,
                "Type": row.Type,
                "Processor": row.Processor,
                "Memory": row.Memory,
                "Graphics": row.Graphics,
                "Storage": row.Storage
            }
            requirements_list.append(requirement)

        return jsonify(requirements_list)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
