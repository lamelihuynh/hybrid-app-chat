"""
WebSocket Handler for P2P Signaling
Manages WebSocket connections for real-time P2P peer discovery and signaling
"""
import asyncio
import websockets
import json
import time
from urllib.parse import parse_qs, urlparse

class WebSocketHandler:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.connections = {}  # {username: websocket}
        self.connection_requests = {} # queue 
        self.ice_candidates = {}
        
    async def handle_client(self, websocket):
        """
        ⭐ CHÚ Ý: CHỈ CÓ 1 PARAMETER (websocket), KHÔNG CÓ path
        Handle WebSocket connection from client
        websockets >= 12.0 chỉ truyền websocket object
        """
        username = None
        
        try:
            # ⭐ LẤY PATH TỪ websocket object
            path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
            
            # Parse query parameters
            parsed = urlparse(path)
            query = parse_qs(parsed.query)
            username = query.get('username', [None])[0]
            
            if not username:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Username required'
                }))
                await websocket.close()
                return
            
            print(f"[WebSocket] Client connected: {username}")
            
            # Store connection
            self.connections[username] = websocket
            
            # Send confirmation
            await websocket.send(json.dumps({
                'type': 'registered',
                'username': username,
                'message': 'WebSocket connected successfully'
            }))
            
            # Notify other peers
            await self.broadcast_peer_status(username, 'online')
            
            # Main message loop
            async for message in websocket:
                await self.handle_message(username, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"[WebSocket] Client disconnected: {username}")
            
        except Exception as e:
            print(f"[WebSocket] Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if username and username in self.connections:
                del self.connections[username]
                await self.broadcast_peer_status(username, 'offline')
                print(f"[WebSocket] Cleaned up: {username}")
    
    async def handle_message(self, username, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            print(f"[WebSocket] {username} → {msg_type}")
            
            if msg_type == 'heartbeat':
                await self.send_to_client(username, {
                    'type': 'heartbeat_ack',
                    'timestamp': time.time()
                })
                
            elif msg_type == 'connection_request':
                await self.handle_connection_request(username, data)
                
            elif msg_type == 'connection_answer':
                await self.handle_connection_answer(username, data)
                
            elif msg_type == 'ice_candidate':
                await self.handle_ice_candidate(username, data)
                
            elif msg_type == 'get_peer_list':
                await self.send_peer_list(username)
                
        except json.JSONDecodeError:
            print(f"[WebSocket] Invalid JSON from {username}")
        except Exception as e:
            print(f"[WebSocket] Error handling message: {e}")
    
    async def handle_connection_request(self, from_username, data):
        """Forward WebRTC offer to target peer"""
        to_username = data.get('to_username')
        offer = data.get('offer')
        
        if not to_username or not offer:
            await self.send_to_client(from_username, {
                'type': 'error',
                'message': 'Invalid connection request'
            })
            return
        
        print(f"[WebSocket] Offer: {from_username} → {to_username}")
        
        
        # Check if Target peer is Online 
        if to_username in self.connections:
            await self.send_to_client(to_username, {
                'type': 'connection_request',
                'from_username': from_username,
                'offer': offer,
                'timestamp': time.time()
            })
            
            await self.send_to_client(from_username, {
                'type': 'request_sent',
                'to_username': to_username,
                'message': 'Connection request sent'
            })
        else:
            await self.send_to_client(from_username, {
                'type': 'error',
                'message': f'Peer {to_username} is offline'
            })
    
    async def handle_connection_answer(self, from_username, data):
        """Forward WebRTC answer to target peer"""
        to_username = data.get('to_username')
        answer = data.get('answer')
        
        if not to_username or not answer:
            await self.send_to_client(from_username, {
                'type': 'error',
                'message': 'Invalid connection answer'
            })
            return
        
        print(f"[WebSocket] Answer: {from_username} → {to_username}")
        
        if to_username in self.connections:
            await self.send_to_client(to_username, {
                'type': 'connection_answer',
                'from_username': from_username,
                'answer': answer,
                'timestamp': time.time()
            })
        else:
            await self.send_to_client(from_username, {
                'type': 'error',
                'message': f'Peer {to_username} is offline'
            })
    
    async def handle_ice_candidate(self, from_username, data):
        """Forward ICE candidate to target peer"""
        to_username = data.get('to_username')
        candidate = data.get('candidate')
        
        if not to_username or not candidate:
            return
        
        print(f"[WebSocket] ICE: {from_username} → {to_username}")
        
        if to_username in self.connections:
            await self.send_to_client(to_username, {
                'type': 'ice_candidate',
                'from_username': from_username,
                'candidate': candidate,
                'timestamp': time.time()
            })
    
    async def send_peer_list(self, username):
        """Send list of online peers"""
        try:
            peers = self.session_manager.get_all_peers()
            
            # Filter out requesting user
            peers = [p for p in peers if p.get('username') != username]
            
            await self.send_to_client(username, {
                'type': 'peer_list',
                'peers': peers,
                'count': len(peers)
            })
        except Exception as e:
            print(f"[WebSocket] Error sending peer list: {e}")
    
    async def send_to_client(self, username, message):
        """Send message to specific client"""
        if username in self.connections:
            try:
                await self.connections[username].send(json.dumps(message))
            except Exception as e:
                print(f"[WebSocket] Error sending to {username}: {e}")
    
    async def broadcast_peer_status(self, username, status):
        """Broadcast peer online/offline status to all clients"""
        message = {
            'type': f'peer_{status}',
            'username': username,
            'timestamp': time.time()
        }
        
        for client_username, websocket in list(self.connections.items()):
            if client_username != username:
                try:
                    await websocket.send(json.dumps(message))
                except Exception as e:
                    print(f"[WebSocket] Broadcast error: {e}")
    
    async def broadcast_to_all(self, message, exclude=None):
        """Broadcast message to all connected clients"""
        for username, websocket in list(self.connections.items()):
            if exclude and username == exclude:
                continue
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                print(f"[WebSocket] Error broadcasting: {e}")