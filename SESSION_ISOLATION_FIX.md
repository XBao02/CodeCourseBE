# Session Isolation Fix - User-Specific Chat Sessions

## 🎯 Problem Addressed

**Before:** Chat sessions were stored using only `session_id` as the key, which meant:
- Sessions could potentially conflict between different users
- If two users somehow got the same session ID, they'd share history
- No validation that the user accessing a session was the owner
- Security risk: anyone with a session ID could access that conversation

**After:** Sessions are now isolated per user account using composite keys `(user_id, session_id)`:
- Each user has their own namespace of sessions
- Sessions cannot be accessed across accounts
- Authentication is required for all session operations
- Users can have multiple sessions (e.g., different devices/browsers)

## 🔧 Changes Made

### 1. **Session Storage Structure** (`Student.py`)

```python
# OLD:
_AI_CHAT_SESSIONS = {}  # session_id -> {user_id, history, created_at}

# NEW:
_AI_CHAT_SESSIONS = {}  # (user_id, session_id) -> {history, created_at}
```

**Key Changes:**
- Composite key `(user_id, session_id)` ensures isolation
- Removed `user_id` from session data (now part of the key)
- Each user can have multiple sessions without conflict

### 2. **Chat Initialization Endpoint**

**Endpoint:** `POST /api/student/recommend/chat/init`

**Changes:**
```python
# OLD:
session_id = str(uuid.uuid4())
_AI_CHAT_SESSIONS[session_id] = { 'user_id': user_id, 'history': [], ... }

# NEW:
session_id = str(uuid.uuid4())
session_key = (user_id, session_id)
_AI_CHAT_SESSIONS[session_key] = { 'history': [], 'created_at': time.time() }
```

**Improvements:**
- ✅ Requires authentication (returns 401 if no token)
- ✅ Uses composite key for storage
- ✅ Logs session creation for debugging
- ✅ Returns session_id to client (client doesn't need to know about user_id in key)

### 3. **Chat Message Endpoint**

**Endpoint:** `POST /api/student/recommend/chat/message`

**Changes:**
```python
# OLD:
if session_id not in _AI_CHAT_SESSIONS:
    return error

# NEW:
user_id = _resolve_user_id_from_identity(get_jwt_identity())
session_key = (user_id, session_id)
if session_key not in _AI_CHAT_SESSIONS:
    return error
```

**Security Improvements:**
- ✅ Verifies user identity from JWT token
- ✅ Builds composite key from authenticated user_id + session_id
- ✅ Validates session belongs to the current user
- ✅ Returns clear error if session doesn't exist or expired
- ✅ Enhanced logging for debugging

### 4. **Session Cleanup Function**

```python
def _cleanup_old_sessions():
    """Remove sessions older than _SESSION_TIMEOUT."""
    current_time = time.time()
    to_remove = []
    for session_key, session_data in _AI_CHAT_SESSIONS.items():
        if current_time - session_data.get('created_at', 0) > _SESSION_TIMEOUT:
            to_remove.append(session_key)
    
    for session_key in to_remove:
        user_id, session_id = session_key  # Unpack composite key
        del _AI_CHAT_SESSIONS[session_key]
        logging.info(f"🧹 Removed expired session {session_id} for user {user_id}")
```

**Improvements:**
- ✅ Unpacks composite keys correctly
- ✅ Logs which user's session was cleaned up
- ✅ Uses proper logging module instead of print

### 5. **Logging Improvements**

Added `import logging` and replaced `print` statements with proper logging:

```python
import os, uuid, time, logging  # Added logging

# Throughout the code:
logging.info(f"✅ Created session {session_id} for user {user_id}")
logging.warning(f"❌ Invalid session {session_id} for user {user_id}")
logging.error(f'Error processing course {cid}: {e}')
```

## 🔒 Security Benefits

1. **Session Hijacking Prevention**
   - Users can only access their own sessions
   - Session IDs alone are useless without authentication
   - Composite key prevents accidental or malicious cross-user access

2. **Authentication Required**
   - Both endpoints now require valid JWT token
   - Returns 401 if user not authenticated
   - User ID is extracted from verified token

3. **Session Validation**
   - Every message request validates session ownership
   - Clear error messages for expired/invalid sessions
   - No information leakage about other users' sessions

4. **Audit Trail**
   - All session creation/access is logged
   - Failed attempts are logged with user context
   - Easier to debug and monitor for suspicious activity

## 📝 API Behavior

### Initialize Chat Session

**Request:**
```bash
POST /api/student/recommend/chat/init
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "sessionId": "uuid-here",
  "message": "Xin chào! Bạn muốn học gì?..."
}
```

**Errors:**
- `401` - Authentication required (no token or invalid token)

### Send Chat Message

**Request:**
```bash
POST /api/student/recommend/chat/message
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "sessionId": "uuid-from-init",
  "message": "Tôi muốn học Python backend"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "same-uuid",
  "reply": "AI response text...",
  "coursesWithReasons": [
    {
      "course": { "id": 1, "title": "...", ... },
      "reason": "This course is perfect because..."
    }
  ],
  "followUp": "Would you like more details?"
}
```

**Errors:**
- `401` - Authentication required
- `400` - Session ID required / Invalid or expired session / Empty message
- `500` - Internal server error

## 🧪 Testing Scenarios

### Test 1: Normal Flow (Same User)
```python
# 1. User A logs in and gets token_A
# 2. User A initializes chat -> session_A
# 3. User A sends messages with session_A -> ✅ Works
# 4. User A can continue conversation -> ✅ Works
```

### Test 2: Session Isolation (Different Users)
```python
# 1. User A initializes chat -> session_A
# 2. User B logs in with different account
# 3. User B tries to use session_A -> ❌ 400 Invalid session
# 4. User B initializes own chat -> session_B
# 5. Both users can chat independently -> ✅ Works
```

### Test 3: Multi-Device Support
```python
# 1. User A logs in on Device 1 -> token_A1, session_A1
# 2. User A logs in on Device 2 -> token_A2, session_A2
# 3. Device 1 uses session_A1 -> ✅ Works
# 4. Device 2 uses session_A2 -> ✅ Works
# 5. Device 1 cannot access session_A2 from Device 2 -> ❌ Different sessions
```

### Test 4: Session Expiration
```python
# 1. User A creates session
# 2. Wait > SESSION_TIMEOUT (1 hour)
# 3. Try to send message -> ❌ 400 Invalid or expired session
# 4. Initialize new session -> ✅ Works
```

## 🚀 Migration Notes

**Backward Compatibility:**
- ⚠️ **Breaking Change**: Old sessions in memory will be invalidated
- Server restart required to apply changes
- Users will need to start new chat sessions
- No data loss (sessions were in-memory only)

**Deployment Checklist:**
1. ✅ Back up current code
2. ✅ Apply changes to `Student.py`
3. ✅ Test authentication flow
4. ✅ Restart Flask server
5. ✅ Test chat initialization and messaging
6. ✅ Verify session isolation between users
7. ✅ Check logs for proper logging

## 🔮 Future Enhancements

### Short-term (Recommended)
1. **Persist Sessions to Database**
   - Store sessions in Redis or PostgreSQL
   - Enable session persistence across server restarts
   - Support multi-server deployments

2. **Session Management Endpoints**
   - `GET /api/student/recommend/chat/sessions` - List user's active sessions
   - `DELETE /api/student/recommend/chat/session/{id}` - Delete specific session
   - `DELETE /api/student/recommend/chat/sessions` - Clear all user sessions

3. **Session Metadata**
   - Track session title/summary
   - Last message timestamp
   - Message count per session

### Long-term (Optional)
1. **Session History Export**
   - Allow users to download chat history
   - Export as JSON or PDF

2. **Session Sharing** (Optional)
   - Share specific sessions with instructors for help
   - Generate shareable link with expiry

3. **Analytics**
   - Track popular queries
   - Monitor AI recommendation accuracy
   - User engagement metrics

## 📊 Monitoring

**Key Metrics to Monitor:**
- Number of active sessions per user
- Session creation rate
- Session expiration rate
- Failed session access attempts
- Average session duration

**Log Messages to Watch:**
```
✅ Created session {session_id} for user {user_id}
💬 User {user_id} sent message in session {session_id}
✅ AI replied to user {user_id} with {count} courses
🧹 Removed expired session {session_id} for user {user_id}
❌ Invalid session {session_id} for user {user_id}
```

## ✅ Verification

Run these checks to verify the fix:

1. **Check imports:**
   ```bash
   grep "import logging" backend/app/routes/Student.py
   ```

2. **Check session structure:**
   ```bash
   grep "_AI_CHAT_SESSIONS = {}" backend/app/routes/Student.py
   ```

3. **Test authentication:**
   ```bash
   curl -X POST http://localhost:5000/api/student/recommend/chat/init
   # Should return 401
   ```

4. **Test with valid token:**
   ```bash
   curl -X POST http://localhost:5000/api/student/recommend/chat/init \
     -H "Authorization: Bearer YOUR_TOKEN"
   # Should return 200 with sessionId
   ```

## 🎓 Summary

This fix ensures that:
- ✅ Each user's chat sessions are completely isolated
- ✅ Authentication is required for all chat operations
- ✅ Session IDs cannot be guessed or hijacked
- ✅ Multiple devices/sessions per user are supported
- ✅ Proper logging and error handling throughout
- ✅ Clean session cleanup prevents memory leaks
- ✅ Clear error messages for troubleshooting

The AI recommendation chat is now secure and production-ready! 🚀
