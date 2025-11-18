/**
 * P2P Agent - Using Websocket 
 * Using websocket for signaling and WebRTC for P2P connection 
 */

class P2PAgent{
    constructor(username, trackers = ['http://127.0.0.1:9001']){
        this.username = username;
        this.trackers = trackers; 
        this.activeTracker = null; 
        this.myPeerInfo = null; 
        this.peers = new Map(); // {username : peerConnection}
        this.messageHandlers = []

        // Adding Websocket 
        this.ws = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttampts = 5; 
        this.reconnectDelay = 2000;

        // WebRTC configuration 
        this.rtcConfig = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };


        this.started = false; 
    }


    /**
     * Start P2P agent with WebSocket 
     */
    async start (){
        console.log('[P2P Agent] Starting with WebSocket...');

        // Connect to tracker
        if (! await this.connectToTracker()){
            console.error('[P2P Agent] Failed to connect to any tracker');
            return false; 
        }

        // Register self with tracker
        if (! await this.registerWithTracker()){
            console.error('[P2P Agent] Failed to register with tracker');
            return false; 
        }

        // Establish websocket connection 
        if (! await this.connectWebSocket()){
            console.error('[P2P Agent] Failed to etablish WebSocket connection');
            return false; 
        }

        // Heart beat (keep-alive)
        this.startHeartbeat();

        this.started = true;
        console.log('[P2P Agent] Started successfully with WebSocket'); 
        return true; 
    }

    async connectToTracker(){
        for (const tracker of this.trackers){
            try{
                const response = await fetch(`${tracker}/ping` , {
                    method: 'GET',
                    credentials: 'include', 
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok){
                    this.activeTracker = tracker; 
                    console.log(`P2P Agent] Connected to tracker: ${tracker}`); 
                    return true; 
                }
            } catch(error){
                console.error(`[P2P Agent] Tracker ${tracker} unavailable:`, error);
            }
        }
        return false;
    }

    /**
     * Register peer info with tracker
     */
    async registerWithTracker(){
        try{
            const localIP = await this.getLocalIP(); 
            const localPort = Math.floor(Math.random()*10000) + 50000;

            const response = await fetch(`${this.activeTracker}/submit-info`, {
                method: 'POST',
                headers: {'Content-Type' : 'application/json'},
                credentials: 'include',
                body: JSON.stringify({
                    ip: localIP, 
                    port: localPort,
                    capabilities: ['webrtc', 'websocket']
                })
            }); 
            const text = await response.text(); 
            let data; 
            try{
                data = JSON.parse (text);
            } catch(e) {
                console.error('[P2P Agent] Failed to parse response: ', text);
                return false;
            }

            if (data.body && typeof data.body == 'string'){
                try{
                    data = JSON.parse(data.body);
                } catch (e){
                    console.error('[P2P Agent] Failed to parse body: ', data.body);
                    return false;
                }
            }

            if (data.status === 'success'){
                this.myPeerInfo = {
                    username: this.username,
                    ip: localIP,
                    port: localPort
                };
                console.log('[P2P Agent] Registered:', this.myPeerInfo);
                return true;
            }

            console.error('[P2P Agent] Registration failed:', data);
            return false;
        } catch(error){
            console.error('[P2P Agent] Registration error:', error );
            return false;
        }
    }

    async connectWebSocket(){
    return new Promise((resolve, reject) => {
        try{
            // ⭐ SỬA: PARSE PORT VÀ THÊM +100
            const url = new URL(this.activeTracker);
            const httpPort = parseInt(url.port) || 9001;
            const wsPort = httpPort + 100;  // WebSocket port = HTTP port + 100
            
            const wsEndpoint = `ws://${url.hostname}:${wsPort}/ws/p2p?username=${this.username}`;
            
            console.log(`[P2P Agent] Connecting WebSocket to: ${wsEndpoint}`);

            this.ws = new WebSocket(wsEndpoint);

            this.ws.onopen = () => {
                console.log('[P2P Agent] WebSocket connected');
                this.wsReconnectAttempts = 0;

                this.ws.send(JSON.stringify({
                    type: 'register',
                    username: this.username,
                    peer_info: this.myPeerInfo
                }));
                resolve(true);
            };

            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };

            this.ws.onerror = (error) => {
                console.error('[P2P Agent] WebSocket error:', error);
                reject(error);
            };

            this.ws.onclose = (event) => {
                console.warn('[P2P Agent] WebSocket closed:', event.code, event.reason);
                this.handleWebSocketClose();
            };

            setTimeout(() => {
                if (this.ws.readyState !== WebSocket.OPEN){
                    this.ws.close();
                    reject(new Error('WebSocket connection timeout'));
                }
            }, 5000); 
        } catch (error){
            console.error('[P2P Agent] Failed to create WebSocket:', error);
            reject(error);
        }
    });
}

    handleWebSocketMessage(data){
        try{
            const message = JSON.parse(data); 
            console.log('[P2P Agent] WebSocket message:', message );
            switch (message.type){
                case 'registered':
                    console.log('[P2P Agent] Successfully registered via WebSocket');
                    break;
                case 'connection_request':
                    this.handleConnectionRequest(message);
                    break;
                case 'connection_answer':
                    this.handleConnectionAnswer(message);
                    break;
                case 'ice_candidate':
                    this.handleIceCandidate(message);
                    break;
                case 'peer_online':
                    console.log(`[P2P Agent] Peer ${message.username} came online`);
                    this.notifyConnectionStatus(message.username, 'online'); 
                    break;
                case 'peer_offline':
                    console.log(`[P2P Agent] Peer ${message.username} went offline`);
                    this.notifyConnectionStatus(message.username, 'offline');
                    this.disconnectFromPeer(message.username);
                    break;
                case 'peer_list':
                    console.log('[P2P Agent] Received peer list:', message.peers);
                    break;
                case 'error':
                    console.error('[P2P Agent] Server error:', message.message);
                    break;
                case 'request_sent':
                    console.log(`[P2P Agent] Connection request sent to ${message.to_username}`);
                    break;

                default:
                    console.warn('[P2P Agent] Unknown message type:', message.type);

            }
        } catch (error){
                console.error('[P2P Agent] Failed to parse WebSocket message:', error);
        }
    }

    handleWebSocketClose() {
        if (!this.started){
            return; 
        }

        if (this.wsReconnectAttempts < this.maxReconnectAttampts){
            this.wsReconnectAttempts++;
            const delay = this.reconnectDelay * this.wsReconnectAttempts;

            console.log(`[P2P Agent] Reconnecting WebSocket ${delay}ms (attempt ${this.wsReconnectAttempts}/${this.maxReconnectAttampts}))`);
            setTimeout(()=> {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('[P2P Agent] Max reconnection attempts reached'); 
            this.notifyConnectionStatus('self', 'disconnected');
        }
    }

  

    /**
     * Get local IP address using WebRTC
     */
    async getLocalIP(){
        return new Promise((resolve) => {
            const pc = new RTCPeerConnection(this.rtcConfig);

            pc.createDataChannel('');

            pc.createOffer().then(offer => pc.setLocalDescription(offer));

            pc.onicecandidate = (ice) => {
                if (!ice || !ice.candidate || !ice.candidate.candidate) {
                    resolve('127.0.0.1');
                    return; }
                
                const ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
                const match = ipRegex.exec(ice.candidate.candidate);
                if (match) {
                    resolve(match[1]);
                    pc.close(); 
                } else {
                    resolve('127.0.0.1');
                }
            };

            setTimeout(() => {
                pc.close();
                resolve('127.0.0.1');
            }, 2000 );
        }); 
    }

    //HANDLE INCOMING CONNECTION REQUEST (VIA WEBSOCKET)

    async handleConnectionRequest(request){
        console.log(`[P2P Agent] Connection request from ${request.from_username}`); 
        try{
            const pc = new RTCPeerConnection(this.rtcConfig);
            // const dataChannel = pc.createDataChannel('p2p-channel');
 
            // Srore pending connection 
            this.peers.set (request.from_username, {
                pc, 
                dataChannel: null, 
                status: 'connecting'});

            // Set up callbacks after get DATACHANNEL

            pc.ondatachannel = (event) => {
                console.log(`[P2P Agent] DataChannel received from ${request.from_username}`); 
                const dataChannel = event.channel; 

                const peer = this.peers.get(request.from_username);
                if (peer){
                    peer.dataChannel = dataChannel; 
                } 

                dataChannel.onopen = () =>{
                    console.log(`[P2P Agent] DataChannel  OPEN with${request.from_username}`);
                    const peer = this.peers.get(request.from_username);
                    if (peer){ 
                        peer.status = 'connected';
                    }
                    this.notifyConnectionStatus(request.from_username, 'connected');
                
                    }; 
                
                dataChannel.onmessage = (event) => {
                    console.log(`[P2P Agent] Message from ${request.from_username}:`, event.data);
                    this.handleP2PMessage(request.from_username, event.data);
                };

                dataChannel.onclose = () => {
                    console.log(`[P2P Agent] DataChannel closed with ${request.from_username}`);
                    this.notifyConnectionStatus(request.from_username, 'disconnected');   
                };

            };


            // ICE candidate handling
            pc.onicecandidate = (event)  =>{
                if (event.candidate){
                    this.sendWebSocketMessage({
                        type: 'ice_candidate',
                        to_username: request.from_username,
                        candidate: event.candidate
                    });
                }
            }; 
             // Set remote offer
            console.log(`[P2P Agent] Setting remote offer from ${request.from_username}`);
            await pc.setRemoteDescription(new RTCSessionDescription(request.offer));
            
            // Create answer
            console.log(`[P2P Agent] Creating answer for ${request.from_username}`);
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            
            // Send answer via WebSocket
            this.sendWebSocketMessage({
                type: 'connection_answer',
                to_username: request.from_username,
                answer: answer
            });

        } catch (error){
            console.error('[P2P Agent] Error handling connection request:', error);
            this.notifyConnectionStatus(request.from_username, 'error');
        }
    }

      async handleConnectionAnswer(message) {
        console.log(`[P2P Agent] Received answer from ${message.from_username}`);
        
        const peer = this.peers.get(message.from_username);
        
        if (!peer || !peer.pc) {
            console.error(`[P2P Agent] No pending connection for ${message.from_username}`);
            return;
        }
        
        try {
            await peer.pc.setRemoteDescription(new RTCSessionDescription(message.answer));
            console.log(`[P2P Agent] Connection established with ${message.from_username}`);
        } catch (error) {
            console.error(`[P2P Agent] Failed to set remote description:`, error);
            this.notifyConnectionStatus(message.from_username, 'error');
        }
    }

     async handleIceCandidate(message) {
        console.log(`[P2P Agent] Received ICE candidate from ${message.from_username}`);
        
        const peer = this.peers.get(message.from_username);
        
        if (!peer || !peer.pc) {
            console.warn(`[P2P Agent] No peer connection for ${message.from_username}`);
            return;
        }
        
        try {
            await peer.pc.addIceCandidate(new RTCIceCandidate(message.candidate));
        } catch (error) {
            console.error(`[P2P Agent] Failed to add ICE candidate:`, error);
        }
    }

    sendWebSocketMessage(message) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('[P2P Agent] WebSocket not connected');
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error('[P2P Agent] Failed to send WebSocket message:', error);
            return false;
        }
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.sendWebSocketMessage({ type: 'heartbeat' });
            }
        }, 30000);  // Every 30 seconds
    }

    async connectToPeer(targetUsername) {
        console.log(`[P2P Agent] Connecting to ${targetUsername}...`);
        
        try {
            // 1. Create WebRTC peer connection
            const pc = new RTCPeerConnection(this.rtcConfig);
            const dataChannel = pc.createDataChannel('p2p-channel');
            
            // Store pending connection
            this.peers.set(targetUsername, { pc, dataChannel, status: 'connecting' });
            
            // 2. Setup data channel callbacks
            dataChannel.onopen = () => {
                console.log(`[P2P Agent] P2P connected to ${targetUsername}`);
                const peer = this.peers.get(targetUsername);
                if (peer) {
                    peer.status = 'connected';
                }
                this.notifyConnectionStatus(targetUsername, 'connected');
            };
            
            dataChannel.onmessage = (event) => {
                this.handleP2PMessage(targetUsername, event.data);
            };
            
            dataChannel.onerror = (error) => {
                console.error(`[P2P Agent] Data channel error:`, error);
                this.notifyConnectionStatus(targetUsername, 'error');
            };
            
            dataChannel.onclose = () => {
                console.log(`[P2P Agent] Disconnected from ${targetUsername}`);
                this.peers.delete(targetUsername);
                this.notifyConnectionStatus(targetUsername, 'disconnected');
            };
            
            // 3. ICE candidate handling
            pc.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendWebSocketMessage({
                        type: 'ice_candidate',
                        to_username: targetUsername,
                        candidate: event.candidate
                    });
                }
            };
            
            // 4. Create offer
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            
            // 5. Send offer via WebSocket
            this.sendWebSocketMessage({
                type: 'connection_request',
                to_username: targetUsername,
                offer: offer
            });
            
            console.log(`[P2P Agent] Connection request sent to ${targetUsername}`);
            return true;
            
        } catch (error) {
            console.error(`[P2P Agent] Failed to connect to ${targetUsername}:`, error);
            this.notifyConnectionStatus(targetUsername, 'error');
            this.peers.delete(targetUsername);
            return false;
        }
    }

    sendToPeer(targetUsername, message) {
        const peer = this.peers.get(targetUsername);
        
        if (!peer || !peer.dataChannel || peer.dataChannel.readyState !== 'open') {
            console.error(`[P2P Agent] Not connected to ${targetUsername}`);
            return false;
        }
        
        try {
            const data = JSON.stringify({
                type: 'message',
                from: this.username,
                message: message,
                timestamp: Date.now()
            });
            
            peer.dataChannel.send(data);
            console.log(`[P2P Agent] Message sent to ${targetUsername} (P2P)`);
            return true;
        } catch (error) {
            console.error(`[P2P Agent] Failed to send message:`, error);
            return false;
        }
    }

     broadcastToPeers(message) {
        console.log(`[P2P Agent] Broadcasting to ${this.peers.size} peers...`);
        
        let successCount = 0;
        
        for (const [username, peer] of this.peers.entries()) {
            if (peer.status === 'connected' && this.sendToPeer(username, message)) {
                successCount++;
            }
        }
        
        console.log(`[P2P Agent] Broadcast sent to ${successCount}/${this.peers.size} peers`);
        return successCount;
    }

     handleP2PMessage(fromUsername, data) {
        try {
            const message = JSON.parse(data);
            console.log(`[P2P Agent] Message from ${fromUsername}:`, message);
            
            this.messageHandlers.forEach((handler, index) => {
                console.log(`[P2P Agent] 📢 Calling handler #${index}`);
                try {
                    handler(fromUsername, message);
                } catch (e){
                    console.error(`[P2P Agent] Handler #${index} error:`, e);

                }
            });
        } catch (error) {
            console.error('[P2P Agent] Failed to parse message:', error);
        }
    }

    onMessage(handler) {
        this.messageHandlers.push(handler);
    }

    notifyConnectionStatus(username, status) {
        window.dispatchEvent(new CustomEvent('p2p-connection-status', {
            detail: { username, status }
        }));
    }

     async getPeerList() {
        return new Promise((resolve) => {
            // Send request via WebSocket
            this.sendWebSocketMessage({ type: 'get_peer_list' });
            
            // Listen for response (temporary)
            const handler = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'peer_list') {
                        this.ws.removeEventListener('message', handler);
                        resolve(message.peers || []);
                    }
                } catch (e) {
                    // Ignore
                }
            };
            
            if (this.ws) {
                this.ws.addEventListener('message', handler);
            }
            
            // Timeout after 5 seconds
            setTimeout(() => {
                if (this.ws) {
                    this.ws.removeEventListener('message', handler);
                }
                resolve([]);
            }, 5000);
        });
    }
    

    disconnectFromPeer(username) {
        const peer = this.peers.get(username);
        
        if (peer) {
            if (peer.dataChannel) {
                peer.dataChannel.close();
            }
            if (peer.pc) {
                peer.pc.close();
            }
            this.peers.delete(username);
            console.log(`[P2P Agent] Disconnected from ${username}`);
        }
    }
    
    stop() {
        this.started = false;
        
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        // Clear intervals
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        // Close all peer connections
        for (const [username, peer] of this.peers.entries()) {
            this.disconnectFromPeer(username);
        }
        
        console.log('[P2P Agent] Stopped');
    }
}


window.p2pAgent = null 
async function initializeP2PAgent(username, trackers) {
    if (window.p2pAgent) {
        window.p2pAgent.stop();
    }
    
    window.p2pAgent = new P2PAgent(username, trackers);
    const success = await window.p2pAgent.start();
    
    if (success) {
        console.log('[P2P] Agent initialized successfully with WebSocket');
    } else {
        console.error('[P2P] Failed to initialize agent');
    }
    
    return success;
}

console.log('[P2P Agent] WebSocket module loaded');