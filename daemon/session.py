import time
import uuid
import threading

class SessionManager:
    """
    Manage Session and tracking peers for P2P application.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.sessions = {}   # {session_token: {username: created_at}}
        self.username_to_token = {} # {username: session_token}
        self.active_peers = {} # {session_token: {username, ip, port, registerd_at}}
        self.user_peer_lists = {} # {session_token: [{peer_ip, peer_port, added_at}]}
    
    def create_session(self, username):
        """
        Create session after login successfully
        """
        with self.lock:
            # Remove old session if exists
            if username in self.username_to_token: 
                old_token = self.username_to_token[username]
                if old_token in self.sessions:
                    del self.sessions[old_token]
                if old_token in self.active_peers: 
                    del self.active_peers[old_token]
            # Create new session
            session_token = str(uuid.uuid4())
            self.sessions[session_token] = {
                'username': username,
                'created_at': time.time(),
                'last_active': time.time(),
                'peer_info': None  
            }
            
            self.username_to_token[username] = session_token
            
            # Initialize empty peer list
            self.user_peer_lists[session_token] = [] 
            
            print(f"[SessionManager] Session created: {username}: {session_token}")
            return session_token
    
    def validate_session(self, session_token):
        """Check if session is valid."""
        with self.lock:
            if session_token in self.sessions:
                self.sessions[session_token]['last_active'] = time.time()
                return True
            return False
    
    def get_session(self, session_token):
        """Get session info."""
        with self.lock:
            return self.sessions.get(session_token)
    
    def submit_peer_info(self, session_token, peer_ip, peer_port):
        """
        Submit peer P2P info (IP:Port of P2P listener)
        
        :param session_token:  Session token
        :param peer_ip: IP of P2P listener
        :param peer_port: Port of P2P listener
        :return: True if successful
        """
        with self.lock:
            if session_token not in self.sessions:
                return False
            
            username = self.sessions[session_token]['username']
            self.active_peers[session_token] = {
                'username': username,
                'ip': peer_ip,
                'port': peer_port,
                'registered_at': time.time()
            }
            
            print(f"[SessionManager] Peer registered: {username} @ {peer_ip}:{peer_port}")
            return True
    
    def get_all_peers(self):
        """
        Get all active peers 
        
        :return: List of peers
        """
        with self.lock:
            peers = []
            for session_token, peer_info in self.active_peers.items():
                if session_token in self.sessions:
                    peers.append({
                        'username': peer_info['username'],
                        'ip': peer_info['ip'],
                        'port': peer_info['port'],
                        'registered_at': peer_info['registered_at']
                    })
            print(f"[SessionManager] Get all peers: {len(peers)} active")

        return peers
    
    
    
    
    
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