import json
from daemon.weaprous import WeApRous
from daemon.session import session_manager
from daemon.userdb import user_db

app = WeApRous()

@app.route('/hello', methods=['PUT'])
def hello(headers, body):
    """
    Handle greeting via PUT request.

    This route prints a greeting message to the console using the provided headers
    and body.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or message payload.
    """
    return {"message": "Hello my name is NHATLINH"}

@app.route("/register", methods=["POST"])
def register(headers, body):
    """
    Register API: Đăng ký user mới
    """
    try:
        username = body.get("username")
        password = body.get("password")
        email = body.get("email", "")
        full_name = body.get("full_name", "")
        
        if not username or not password:
            return {
                "status": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Username and password are required"
                })
            }
        
        # Đăng ký user
        if user_db.register_user(username, password, email, full_name):
            return {
                "status": 201,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "success",
                    "message": "User registered successfully"
                })
            }
        else:
            return {
                "status": 409,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Username already exists"
                })
            }
    
    except Exception as e:
        print(f"[Register] Error: {e}")
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": "Internal server error"
            })
        }

@app.route("/login", methods=["POST"])
def login(headers, body):
    """
    Login API: Xác thực username/password và tạo session token
    """
    print("[Login] Headers:", headers)
    print("[Login] Body:", body)
    
    try:
        # Parse body để lấy username/password
        username = body.get("username")
        password = body.get("password")
        
        if not username or not password:
            return {
                "status": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Username and password are required"
                })
            }
        
        print(f"[Login] Attempting login for user: {username}")
        
        # Xác thực với database
        if user_db.authenticate(username, password):
            # Tạo session
            session_token = session_manager.create_session(username)
            print(f"[Login] Login successful. Session token: {session_token}")
            
            # Lấy thông tin user
            user_info = user_db.get_user_info(username)
            
            # Trả về response với Set-Cookie header
            response_body = json.dumps({
                "status": "success",
                "message": "Login successful",
                "session_token": session_token,
                "user": {
                    "username": username,
                    "email": user_info.get('email', ''),
                    "full_name": user_info.get('full_name', '')
                }
            })
            
            return {
                "status": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Set-Cookie": f"session_token={session_token}; Path=/; HttpOnly"
                },
                "body": response_body
            }
        else:
            # Sai username hoặc password
            print(f"[Login] Authentication failed for user: {username}")
            return {
                "status": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Invalid username or password"
                })
            }
    
    except Exception as e:
        print(f"[Login] Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": "Internal server error"
            })
        }



@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    print(f"[MyAPI] Submitting info: {body}")
    user_id = body.get('ip')
    user_port = body.get('port')

    return 

@app.route('/add-list', methods=['POST'])
def add_list(headers, body):
    print(f"[MyAPI] Adding to list: {body}")
    # TODO: Xử lý logic thêm vào danh sách
    return 

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    print("[MyAPI] Getting list.")
    # TODO: Xử lý logic lấy danh sách
    return 

@app.route('/connect-peer', methods=['POST'])
def connect_peer(headers, body):
    print(f"[MyAPI] Connecting to peer: {body}")
    # TODO: Xử lý logic kết nối peer
    return 

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_peer(headers, body):
    
    print(f"[MyAPI] Broadcasting to peers: {body}")
    # TODO: Xử lý logic broadcast
    return  

@app.route('/send-peer', methods=['POST'])
def send_peer(headers, body):
    print(f"[MyAPI] Sending to a peer: {body}")
    # TODO: Xử lý logic gửi tin cho peer
    return 