import hashlib
import json
import os
import threading

class UserDatabase:
    """
    Quản lý thông tin người dùng cho authentication.
    Hỗ trợ lưu trữ dạng file JSON hoặc có thể mở rộng sang SQL database.
    """
    def __init__(self, db_file='users.json'):
        self.db_file = db_file
        self.users = {}
        self.lock = threading.Lock()
        self._load_users()
    
    def _load_users(self):
        """Load users từ file JSON"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    self.users = json.load(f)
                print(f"[UserDB] Loaded {len(self.users)} users from {self.db_file}")
            except Exception as e:
                print(f"[UserDB] Error loading users: {e}")
                self.users = {}
        else:
            # Tạo users mặc định
            self._create_default_users()
    
    def _save_users(self):
        """Lưu users vào file JSON"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            print(f"[UserDB] Saved {len(self.users)} users to {self.db_file}")
        except Exception as e:
            print(f"[UserDB] Error saving users: {e}")
    
    def _create_default_users(self):
        """Tạo một số users mặc định để test"""
        default_users = [
            {'username': 'admin', 'password': 'admin123', 'email': 'admin@hcmut.edu.vn'},
            {'username': 'user1', 'password': 'password1', 'email': 'user1@hcmut.edu.vn'},
            {'username': 'nhatlinh', 'password': 'linh123', 'email': 'linh@hcmut.edu.vn'},
        ]
        
        for user in default_users:
            self.register_user(
                user['username'], 
                user['password'], 
                user['email']
            )
        
        self._save_users()
        print(f"[UserDB] Created {len(default_users)} default users")
    
    def _hash_password(self, password):
        """Hash password bằng SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email='', full_name=''):
        """
        Đăng ký user mới.
        
        :param username: Tên đăng nhập (unique)
        :param password: Mật khẩu (sẽ được hash)
        :param email: Email
        :param full_name: Tên đầy đủ
        :return: True nếu thành công, False nếu username đã tồn tại
        """
        with self.lock:
            if username in self.users:
                print(f"[UserDB] Username '{username}' already exists")
                return False
            
            self.users[username] = {
                'password_hash': self._hash_password(password),
                'email': email,
                'full_name': full_name,
                'created_at': __import__('time').time(),
                'is_active': True
            }
            
            self._save_users()
            print(f"[UserDB] User '{username}' registered successfully")
            return True
    
    def authenticate(self, username, password):
        """
        Xác thực username và password.
        
        :param username: Tên đăng nhập
        :param password: Mật khẩu
        :return: True nếu đúng, False nếu sai
        """
        with self.lock:
            if username not in self.users:
                print(f"[UserDB] Username '{username}' not found")
                return False
            
            user = self.users[username]
            
            # Kiểm tra account có active không
            if not user.get('is_active', True):
                print(f"[UserDB] User '{username}' is inactive")
                return False
            
            # So sánh password hash
            password_hash = self._hash_password(password)
            if password_hash == user['password_hash']:
                print(f"[UserDB] User '{username}' authenticated successfully")
                return True
            else:
                print(f"[UserDB] Wrong password for user '{username}'")
                return False
    
    def get_user_info(self, username):
        """Lấy thông tin user (không bao gồm password)"""
        with self.lock:
            if username in self.users:
                user = self.users[username].copy()
                user.pop('password_hash', None)  # Không trả về password hash
                return user
            return None
    
    def update_user(self, username, **kwargs):
        """Cập nhật thông tin user"""
        with self.lock:
            if username not in self.users:
                return False
            
            # Cập nhật các fields được phép
            allowed_fields = ['email', 'full_name', 'is_active']
            for key, value in kwargs.items():
                if key in allowed_fields:
                    self.users[username][key] = value
            
            # Nếu update password
            if 'password' in kwargs:
                self.users[username]['password_hash'] = self._hash_password(kwargs['password'])
            
            self._save_users()
            return True
    
    def delete_user(self, username):
        """Xóa user"""
        with self.lock:
            if username in self.users:
                del self.users[username]
                self._save_users()
                print(f"[UserDB] User '{username}' deleted")
                return True
            return False
    
    def list_users(self):
        """Liệt kê tất cả users (không bao gồm password)"""
        with self.lock:
            users_list = []
            for username, user_data in self.users.items():
                user_info = {
                    'username': username,
                    'email': user_data.get('email', ''),
                    'full_name': user_data.get('full_name', ''),
                    'is_active': user_data.get('is_active', True)
                }
                users_list.append(user_info)
            return users_list

# Global instance
user_db = UserDatabase()