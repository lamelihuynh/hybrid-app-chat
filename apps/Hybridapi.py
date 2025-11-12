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

@app.route("/get-user-info", methods=["GET"])
def get_user_info_api(headers, body):
    """
    Get current user info from session
    """
    print("[GetUserInfo] Headers:", headers)
    
    try:
        # Lấy session token từ cookie
        cookie = headers.get("Cookie", "")
        session_token = None
        
        if cookie:
            for item in cookie.split(";"):
                item = item.strip()
                if item.startswith("session_token="):
                    session_token = item.split("=", 1)[1]
                    break
        
        print(f"[GetUserInfo] Session token: {session_token}")
        
        # Validate session
        if not session_token:
            print("[GetUserInfo] No session token")
            return {
                "status": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Unauthorized - No session token"})
            }
        
        if not session_manager.validate_session(session_token):
            print("[GetUserInfo] Invalid session")
            return {
                "status": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Unauthorized - Invalid session"})
            }
        
        # Get session info
        session = session_manager.get_session(session_token)
        username = session['username']
        
        # Get user info from database
        user_info = user_db.get_user_info(username)
        
        print(f"[GetUserInfo] User: {username}")
        
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "username": username,
                "email": user_info.get('email', ''),
                "full_name": user_info.get('full_name', '')
            })
        }
    
    except Exception as e:
        print(f"[GetUserInfo] Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }


@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    """
    Submit-info API
    
    Request body :
    {
        "ip" : 192.168.1.100,
        "port" : 8000
    }
    """
    print("[SubmitInfo] Headers:", headers)
    print("[SubmitInfo] Body:", body)

    try : 
        cookie = headers.get("Cookie", "") 
        session_token = None
        
        if cookie: 
            for item in cookie.split(";"): 
                item = item.strip() 
                if item.startswith("seesion_token="): 
                    session_token = item.split("=", 1) 
                    break
        if not session_token:
            print("[SubmitInfo] No session token")
            return {
                "status" : 401, 
                "headers": {"Content-Type": "application/json"},
                "body" : json.dumps({
                    "status" : "error",
                    "message" : "Unauthorized - No session token"
                    })
            }
        
        peer_ip = body.get("ip")
        peer_port = body.get("port")
        
        if not peer_ip or not peer_port: 
            print("[SubmitInfo] Missing IP or port")
            return {
                "status": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "IP and port are required"
                })
            }
        

        # Validate port 
        try: 
            peer_port = int(peer_port)
            if peer_port < 0 or peer_port > 65535:
                raise ValueError("Port out of range")
        except(ValueError, TypeError):
            return{
                "status" : 400, 
                "headers": {"Content-Type": "application/json"},
                "body" : json.dumps({
                    "status" : "error",
                    "message" : "Invalid port number (1 - 65535)"
                    })
            }
            
        # Info of user
        session = session_manager.get_session(session_token)
        username = session['username']
    except Exception as e:
        print(f"[SubmitInfo] Error: {e}")
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