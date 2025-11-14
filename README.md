# WeApRous - P2P Chat Application with Authentication

A peer-to-peer chat application with user authentication, channel management, and reverse proxy support built from scratch using Python sockets.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Default User Accounts](#default-user-accounts)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contact](#contact)

## 🎯 Overview

WeApRous is a custom-built web application framework designed for CO3094 course at HCMUT. It implements:
- **Custom HTTP Server** - Built from scratch using Python sockets
- **RESTful API Framework** - Decorator-based routing system
- **User Authentication** - Session-based authentication with SHA256 password hashing
- **P2P Communication** - Peer discovery and connection management
- **Channel System** - Create and join chat channels
- **Reverse Proxy** - Configurable proxy server with load balancing

## ✨ Features

### Authentication & User Management
- ✅ User registration and login
- ✅ Session management with cookies
- ✅ SHA256 password hashing
- ✅ JSON-based user database
- ✅ Thread-safe operations

### Channel Management
- ✅ Create public channels
- ✅ Join existing channels
- ✅ List all available channels
- ✅ View channel members
- ✅ Real-time message sending

### P2P Networking
- ✅ Peer registration (submit-info)
- ✅ Active peer discovery (get-list)
- ✅ Peer-to-peer connections
- ✅ Session tracking

### Reverse Proxy
- ✅ Virtual host configuration
- ✅ Multiple backend support
- ✅ Round-robin load balancing
- ✅ Custom routing rules

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │◄───────►│ Reverse Proxy │◄───────►│  Backend    │
│  (Client)   │         │  (Port 8080)  │         │ (Port 9001) │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Load Balancer│
                        │  (Optional)  │
                        └──────────────┘
```

### Core Components

1. **Backend Server** (`daemon/backend.py`)
   - Multi-threaded TCP server
   - Handles HTTP requests/responses
   - Routes to appropriate handlers

2. **HTTP Adapter** (`daemon/httpadapter.py`)
   - Parses HTTP requests
   - Builds HTTP responses
   - Manages connections

3. **WeApRous Framework** (`daemon/weaprous.py`)
   - Decorator-based routing
   - RESTful API support
   - Request/response handling

4. **Session Manager** (`daemon/session.py`)
   - Session token generation
   - Peer tracking
   - Connection management

5. **User Database** (`daemon/userdb.py`)
   - User authentication
   - Password hashing
   - User CRUD operations

6. **Channel Manager** (`daemon/channel.py`)
   - Channel creation
   - Member management
   - Message routing

## 🔧 Prerequisites

- **Python 3.7+**
- **Web Browser** (Chrome, Safari, Firefox, Edge)
- **Operating System**: macOS, Linux, or Windows
- **Network**: Local network access for P2P features

### Python Packages
No external packages required - uses only Python standard library:
- `socket` - Network communication
- `threading` - Concurrent connections
- `json` - Data serialization
- `hashlib` - Password hashing
- `uuid` - Session token generation

## 📦 Installation

### 1. Clone/Download the Repository
```bash
cd /Users/huynhnhatlinh0305/Downloads/CO3094-weaprous
```

### 2. Verify Python Installation
```bash
python3 --version
# Should output: Python 3.7.x or higher
```

### 3. Check Project Structure
```bash
ls -la
# Should see: daemon/, www/, static/, apps/, config/, etc.
```

### 4. Verify File Permissions
```bash
chmod +x start_sampleapp.py
chmod +x start_proxy.py
```

## 🚀 Running the Application

### Method 1: Direct Run (Recommended)

1. **Start the Backend Server**
   ```bash
   python3 ./start_sampleapp.py
   ```
   
   Output should show:
   ```
   [UserDB] Loaded 3 users from users.json
   [Backend] Listening on port 9001
   [Backend] Active threads will be displayed...
   ```

2. **Access the Application**
   
   Open your browser and navigate to:
   ```
   http://127.0.0.1:9001
   ```

### Method 2: With Custom Port

```bash
python3 ./start_sampleapp.py --server-port 9002
```

### Method 3: With Reverse Proxy

1. **Start the backend**
   ```bash
   python3 ./start_sampleapp.py --server-port 9001
   ```

2. **Start the proxy** (in a new terminal)
   ```bash
   python3 ./start_proxy.py --server-port 8080
   ```

3. **Configure /etc/hosts** (optional, for virtual hosts)
   ```bash
   sudo nano /etc/hosts
   ```
   
   Add:
   ```
   127.0.0.1    app1.local
   127.0.0.1    app2.local
   ```

4. **Access via proxy**
   ```
   http://app1.local:8080
   ```

### Method 4: Using VS Code Debugger

1. Open VS Code
2. Go to Run and Debug (⌘+⇧+D on Mac)
3. Select "Python Debugger for Webapprous"
4. Press F5 to start debugging

## 👤 Default User Accounts

The application comes with **3 pre-registered test accounts**:

| #  | Username   | Password   | Email                    | Role  |
|----|-----------|-----------|--------------------------|-------|
| 1  | admin     | admin123  | admin@hcmut.edu.vn      | Admin |
| 2  | nhatlinh  | linh123   | linh@hcmut.edu.vn       | User  |
| 3  | user1     | password1 | user1@hcmut.edu.vn      | User  |

### Customizing Default Accounts

Edit `daemon/userdb.py` at line 40:

```python
def _create_default_users(self):
    """Create default test users"""
    default_users = [
        {'username': 'your_username', 'password': 'your_password', 'email': 'your_email@domain.com'},
        {'username': 'another_user', 'password': 'another_pass', 'email': 'email@domain.com'},
        # Add more users as needed
    ]
    # ...
```

**After modifying:**
1. Delete `users.json` file (if it exists)
2. Restart the application
3. New default users will be created automatically

## 📁 Project Structure

```
CO3094-weaprous/
├── daemon/                    # Core server modules
│   ├── backend.py            # Multi-threaded HTTP server
│   ├── httpadapter.py        # HTTP request/response handler
│   ├── weaprous.py           # RESTful routing framework
│   ├── request.py            # HTTP request parser
│   ├── response.py           # HTTP response builder
│   ├── session.py            # Session & peer management
│   ├── userdb.py             # User authentication & database
│   ├── channel.py            # Channel management system
│   └── dictionary.py         # Case-insensitive dict utilities
│
├── apps/                      # Application logic
│   └── Hybridapi.py          # REST API endpoints
│
├── www/                       # Web interface
│   ├── index.html            # Landing page
│   ├── login.html            # Login page
│   ├── dashboard.html        # User dashboard
│   └── channels.html         # Chat channels interface
│
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   ├── images/               # Images
│   └── js/                   # JavaScript files
│
├── config/                    # Configuration files
│   └── proxy.conf            # Reverse proxy configuration
│
├── .vscode/                   # VS Code settings
│   └── launch.json           # Debug configurations
│
├── start_sampleapp.py        # Backend server entry point
├── start_proxy.py            # Reverse proxy entry point
├── users.json                # User database (auto-generated)
└── README.md                 # This file
```

## 🔌 API Documentation

### Authentication APIs

#### POST `/register`
Register a new user account.

**Request:**
```json
{
  "username": "newuser",
  "password": "securepass123",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "User registered successfully"
}
```

---

#### POST `/login`
Authenticate user and create session.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "session_token": "abc123-def456-ghi789",
  "user": {
    "username": "admin",
    "email": "admin@hcmut.edu.vn",
    "full_name": ""
  }
}
```

**Sets Cookie:** `session_token={token}; Path=/; HttpOnly`

---

#### GET `/get-user-info`
Get current logged-in user information.

**Headers Required:**
```
Cookie: session_token={your_token}
```

**Response:**
```json
{
  "username": "admin",
  "email": "admin@hcmut.edu.vn",
  "full_name": ""
}
```

---

### P2P APIs

#### POST `/submit-info`
Register peer information for P2P connection.

**Request:**
```json
{
  "ip": "192.168.1.100",
  "port": 8000
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Peer info registered successfully",
  "peer": {
    "username": "admin",
    "ip": "192.168.1.100",
    "port": 8000
  }
}
```

---

#### GET `/get-list`
Get list of all active peers.

**Response:**
```json
{
  "status": "success",
  "peers": [
    {
      "username": "admin",
      "ip": "192.168.1.100",
      "port": 8000,
      "registered_at": 1699999999.123
    }
  ],
  "count": 1
}
```

---

### Channel APIs

#### POST `/create-channel`
Create a new chat channel.

**Request:**
```json
{
  "channel_name": "general"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Channel created successfully",
  "channel": {
    "name": "general",
    "creator": "admin"
  }
}
```

---

#### GET `/list-channels`
Get all available channels.

**Response:**
```json
{
  "status": "success",
  "channels": [
    {
      "name": "general",
      "creator": "admin",
      "members_count": 3,
      "created_at": 1699999999.123
    }
  ]
}
```

---

#### POST `/join-channel`
Join an existing channel.

**Request:**
```json
{
  "channel_name": "general"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Joined channel 'general' successfully",
  "channel": {
    "name": "general",
    "members": ["admin", "user1", "nhatlinh"]
  }
}
```

---

#### POST `/send-message`
Send message to a channel.

**Request:**
```json
{
  "channel_name": "general",
  "message": "Hello everyone!"
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": 1699999999.123
}
```

---

### Error Responses

All APIs return error responses in this format:

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing parameters)
- `401` - Unauthorized (invalid session)
- `404` - Not Found
- `409` - Conflict (already exists)
- `500` - Internal Server Error

## ⚙️ Configuration

### Server Configuration

Edit `start_sampleapp.py`:

```python
PORT = 9001  # Change default port

# Or use command line:
python3 start_sampleapp.py --server-ip 0.0.0.0 --server-port 9002
```

### Proxy Configuration

Edit `config/proxy.conf`:

```nginx
host "192.168.56.103:8080" {
    proxy_pass http://192.168.56.103:9000;
}

host "app1.local:8080" {
    proxy_pass http://127.0.0.1:9001;
}

host "app2.local" {
    proxy_pass http://192.168.56.210:9002;
    proxy_pass http://192.168.56.220:9002;
    
    dist_policy round-robin
}
```

**Supported policies:**
- `round-robin` - Distribute requests evenly
- More policies can be added in `start_proxy.py`

### Database Configuration

The user database is stored in `users.json`. To change location:

```python
# In daemon/userdb.py
user_db = UserDatabase(db_file='path/to/custom/users.json')
```

### Session Configuration

Modify session timeout in `daemon/session.py`:

```python
# Add to Session class
SESSION_TIMEOUT = 3600  # seconds (1 hour)
```

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `[Errno 48] Address already in use`

**Solution:**
```bash
# Find process using the port (macOS/Linux)
lsof -i :9001

# Kill the process
kill -9 <PID>

# Or use a different port
python3 start_sampleapp.py --server-port 9002
```

---

### Cannot Connect to Server

**Symptoms:** Browser shows "Connection refused"

**Solutions:**
1. Check if server is running:
   ```bash
   ps aux | grep start_sampleapp
   ```

2. Verify port:
   ```bash
   netstat -an | grep 9001
   ```

3. Check firewall:
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
   ```

4. Try localhost instead of 127.0.0.1:
   ```
   http://localhost:9001
   ```

---

### Session/Login Issues

**Symptoms:** Always redirected to login page

**Solutions:**
1. Check browser cookies:
   - Open DevTools (F12)
   - Go to Application → Cookies
   - Look for `session_token`

2. Clear cookies and try again:
   ```javascript
   // In browser console
   document.cookie = 'session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
   ```

3. Check console for errors:
   - Open DevTools (F12)
   - Go to Console tab
   - Look for authentication errors

4. Verify `users.json` exists:
   ```bash
   ls -la users.json
   cat users.json  # Check content
   ```

---

### User Database Corrupted

**Symptoms:** Login fails for all users

**Solution:**
```bash
# Backup current database
mv users.json users.json.backup

# Restart server to regenerate
python3 start_sampleapp.py
```

---

### 404 Not Found for API Endpoints

**Symptoms:** API returns 404

**Solutions:**
1. Check route registration in `apps/Hybridapi.py`
2. Verify decorator syntax:
   ```python
   @app.route('/your-endpoint', methods=['POST'])
   ```
3. Check server logs for route registration
4. Restart server after code changes

---

### MIME Type Errors

**Symptoms:** CSS/JS files not loading

**Solution:**
1. Check `static/` directory exists
2. Verify file paths in HTML
3. Check `daemon/response.py` MIME handling
4. Clear browser cache

---

### Thread Errors

**Symptoms:** `RuntimeError: threads can only be started once`

**Solution:**
```bash
# Kill all Python processes
pkill -9 python3

# Restart server
python3 start_sampleapp.py
```

---

### JSON Parse Errors

**Symptoms:** `JSON parse error` in console

**Solutions:**
1. Check request body format
2. Verify `Content-Type: application/json` header
3. Use browser DevTools Network tab to inspect request/response
4. Check server logs for parsing errors

---

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Unauthorized - Invalid session" | Session expired or invalid | Login again |
| "Username already exists" | Duplicate registration | Use different username |
| "Channel name requirement" | Missing channel_name | Provide channel name |
| "Port out of range" | Invalid port number | Use 1-65535 |
| "Internal server error" | Server exception | Check server logs |

---

### Debug Mode

Enable detailed logging:

```python
# Add to start_sampleapp.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View logs:
```bash
python3 start_sampleapp.py 2>&1 | tee server.log
```

---

### Still Having Issues?

1. **Check server logs** - Look for error messages and stack traces
2. **Use browser DevTools** - Inspect network requests and responses
3. **Read the code** - Check `daemon/` modules for implementation details
4. **Contact support** - Email the developer (see Contact section)

## 💻 Development

### Adding New API Endpoints

1. Open `apps/Hybridapi.py`
2. Add new route:

```python
@app.route('/your-endpoint', methods=['POST'])
def your_function(headers, body):
    try:
        # Validate session
        session_token = get_session_token(headers)
        if not session_manager.validate_session(session_token):
            return error_response(401, "Unauthorized")
        
        # Your logic here
        data = body.get("your_param")
        
        # Return response
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "success",
                "data": data
            })
        }
    except Exception as e:
        print(f"[YourFunction] Error: {e}")
        return error_response(500, "Internal server error")
```

### Extending User Database

Add new fields to user records in `daemon/userdb.py`:

```python
self.users[username] = {
    'password_hash': self._hash_password(password),
    'email': email,
    'full_name': full_name,
    'created_at': __import__('time').time(),
    'is_active': True,
    'profile_image': '',  # New field
    'last_login': None    # New field
}
```

### Custom Middleware

Add middleware in `daemon/httpadapter.py`:

```python
def handle_client(self, conn, addr, routes):
    # Add your middleware here
    if not self.check_rate_limit(addr):
        conn.sendall(b"HTTP/1.1 429 Too Many Requests\r\n\r\n")
        return
    
    # Existing code...
```

### Testing

Run manual tests:

```bash
# Test API endpoint
curl -X POST http://127.0.0.1:9001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test with session
curl -X GET http://127.0.0.1:9001/get-user-info \
  -H "Cookie: session_token=YOUR_TOKEN"
```

## 📝 Course Information

**Course:** CO3094 - Computer Networks  
**Institution:** Ho Chi Minh City University of Technology (HCMUT)  
**Instructor:** Dr. Pham Dinh Nguyen  
**Year:** 2025

### Learning Objectives

This project demonstrates:
- ✅ Socket programming and TCP/IP networking
- ✅ HTTP protocol implementation
- ✅ RESTful API design
- ✅ Session management and authentication
- ✅ Multi-threaded server architecture
- ✅ P2P network communication
- ✅ Reverse proxy and load balancing

## 📧 Contact

**Developer:** Huỳnh Nhật Linh  
**Student ID:** [Your Student ID]  
**Email:** gianglinh217@gmail.com

### Reporting Issues

Please include in your report:
- ✉️ Description of the issue
- 📝 Steps to reproduce
- 💻 Error messages and stack traces
- 🖥️ Operating system and Python version
- 📸 Screenshots (if applicable)

### Contributing

This is a course project. For suggestions or improvements:
1. Document your proposed changes
2. Email detailed description
3. Include code examples if applicable

## 📄 License

Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.  
All rights reserved.

This file is part of the CO3093/CO3094 course, and is released under the "MIT License Agreement".

## 🙏 Acknowledgments

- **Dr. Pham Dinh Nguyen** - Course instructor and project framework
- **HCMUT** - Ho Chi Minh City University of Technology
- **VNU-HCM** - Vietnam National University Ho Chi Minh City

---

## 🚀 Quick Start Checklist

- [ ] Python 3.7+ installed
- [ ] Project files downloaded
- [ ] Run `python3 start_sampleapp.py`
- [ ] Open browser to `http://127.0.0.1:9001`
- [ ] Login with default account (admin/admin123)
- [ ] Test dashboard features
- [ ] Create a channel
- [ ] Send messages
- [ ] Register peer info
- [ ] View active peers

---

**Last Updated:** November 14, 2025  
**Version:** 1.0.0  
**Status:** Active Development

**Happy Coding! 🎉**
