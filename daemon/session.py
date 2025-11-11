import time
import uuid
import threading

class SessionManager:
    """
    Quản lý session và tracking peers cho P2P application.
    """
    def __init__(self):
        self.lock = threading.Lock()
        # {session_token: session_data}
        self.sessions = {}
        # {username: session_token}
        self.username_to_token = {}
        # {peer_id: peer_info} - Lưu info từ submit-info
        self.active_peers = {}
    
    def create_session(self, username):
        """Tạo session sau khi login thành công"""
        with self.lock:
            session_token = str(uuid.uuid4())
            self.sessions[session_token] = {
                'username': username,
                'created_at': time.time(),
                'last_active': time.time(),
                'peer_info': None  # Sẽ được cập nhật khi submit-info
            }
            self.username_to_token[username] = session_token
            return session_token
    
    def validate_session(self, session_token):
        """Kiểm tra session có hợp lệ không"""
        with self.lock:
            if session_token in self.sessions:
                self.sessions[session_token]['last_active'] = time.time()
                return True
            return False
    
    def get_session(self, session_token):
        """Lấy thông tin session"""
        with self.lock:
            return self.sessions.get(session_token)
    
    def submit_peer_info(self, session_token, peer_ip, peer_port):
        """
        Lưu thông tin peer từ submit-info API.
        Đây là IP/port mà peer sẽ lắng nghe cho P2P connection.
        """
        with self.lock:
            if session_token not in self.sessions:
                return False
            
            session = self.sessions[session_token]
            peer_id = f"{peer_ip}:{peer_port}"
            
            peer_info = {
                'peer_id': peer_id,
                'ip': peer_ip,
                'port': peer_port,
                'username': session['username'],
                'channels': [],
                'last_seen': time.time()
            }
            
            # Cập nhật peer info vào session
            session['peer_info'] = peer_info
            
            # Lưu vào active peers list
            self.active_peers[peer_id] = peer_info
            
            print(f"[SessionManager] Peer registered: {peer_id} (user: {session['username']})")
            return True
    
    def get_peer_list(self, session_token):
        """Lấy danh sách peers đang active (cho get-list API)"""
        with self.lock:
            if session_token not in self.sessions:
                return None
            
            # Trả về list peers (không bao gồm chính mình)
            current_session = self.sessions[session_token]
            current_peer_id = None
            if current_session['peer_info']:
                current_peer_id = current_session['peer_info']['peer_id']
            
            peer_list = []
            for peer_id, peer_info in self.active_peers.items():
                if peer_id != current_peer_id:
                    peer_list.append({
                        'ip': peer_info['ip'],
                        'port': peer_info['port'],
                        'username': peer_info['username']
                    })
            
            return peer_list
    
    def remove_session(self, session_token):
        """Xóa session khi logout hoặc timeout"""
        with self.lock:
            if session_token in self.sessions:
                session = self.sessions[session_token]
                username = session['username']
                
                # Xóa peer info nếu có
                if session['peer_info']:
                    peer_id = session['peer_info']['peer_id']
                    if peer_id in self.active_peers:
                        del self.active_peers[peer_id]
                        print(f"[SessionManager] Peer removed: {peer_id}")
                
                # Xóa username mapping
                if username in self.username_to_token:
                    del self.username_to_token[username]
                
                # Xóa session
                del self.sessions[session_token]
                print(f"[SessionManager] Session removed: {username}")

# Global instance
session_manager = SessionManager()