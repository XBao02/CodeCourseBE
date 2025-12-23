# Troubleshooting Guide: AI Chat Session Issues

## Common Issues and Solutions

### 1. "Session not found or already expired" Error

**Symptoms:**
- Error appears after sending a message
- Usually occurs after clearing chat history
- Or after the page has been idle for a while

**Solutions:**

#### A. Check Browser Console
Open the browser console (F12) and look for:
```
✅ Chat session initialized: [session-id-here]
📨 Sending message with session: [session-id-here]
```

If you see different session IDs, the session wasn't properly saved.

#### B. Check Backend Logs
In the backend terminal, you should see:
```
✅ Created session [session-id] for user [user-id]
📨 Chat message request - User: [user-id], Session: [session-id]
🔍 Active sessions for user [user-id]: [(user-id, session-id)]
```

If the session isn't in the active sessions list, it was either:
- Not created properly
- Cleared/expired
- The frontend is using a different session ID

#### C. Manual Fix (Frontend)
If the issue persists, try this in the browser console:
```javascript
// Clear local storage
localStorage.removeItem('recoState')

// Refresh the page
location.reload()
```

#### D. Manual Fix (Backend)
If sessions are stuck, restart the backend server:
```powershell
# Stop the server (Ctrl+C)
# Then restart it
cd backend
python app.py
```

---

### 2. Chat History Doesn't Clear

**Symptoms:**
- Click "Clear Chat History"
- Chat appears to clear
- But old messages reappear on refresh

**Solutions:**

#### A. Check localStorage
In browser console:
```javascript
// Check what's stored
console.log(localStorage.getItem('recoState'))

// Clear it manually
localStorage.removeItem('recoState')
```

#### B. Hard Refresh
Do a hard refresh to clear cached state:
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

---

### 3. Multiple Chat Sessions Active

**Symptoms:**
- Backend logs show multiple sessions for one user
- Chat responses are inconsistent

**Solutions:**

#### A. Check Active Sessions (Backend)
Add this temporary endpoint to check sessions:

```python
@student_bp.get('/recommend/chat/debug/sessions')
@jwt_required()
def debug_sessions():
    ident = get_jwt_identity()
    user_id = _resolve_user_id_from_identity(ident)
    
    user_sessions = [
        {'session_id': k[1], 'created_at': v['created_at'], 'message_count': len(v['history'])}
        for k, v in _AI_CHAT_SESSIONS.items()
        if k[0] == user_id
    ]
    
    return jsonify({
        'user_id': user_id,
        'active_sessions': len(user_sessions),
        'sessions': user_sessions
    })
```

Then call it:
```
GET http://localhost:5000/api/student/recommend/chat/debug/sessions
Authorization: Bearer [your-token]
```

#### B. Clear All Sessions for User
Add this temporary endpoint to clear all sessions:

```python
@student_bp.delete('/recommend/chat/debug/clear-all')
@jwt_required()
def debug_clear_all():
    ident = get_jwt_identity()
    user_id = _resolve_user_id_from_identity(ident)
    
    keys_to_delete = [k for k in _AI_CHAT_SESSIONS.keys() if k[0] == user_id]
    for k in keys_to_delete:
        del _AI_CHAT_SESSIONS[k]
    
    return jsonify({
        'success': True,
        'cleared_sessions': len(keys_to_delete)
    })
```

---

### 4. Session Expires Too Quickly

**Symptoms:**
- Session expires after just a few minutes
- Error appears even when actively chatting

**Solutions:**

#### A. Check Cleanup Interval
In `Student.py`, find `_cleanup_old_sessions()`:

```python
def _cleanup_old_sessions(max_age_seconds=3600):  # 1 hour default
    # ...
```

Increase `max_age_seconds` if needed (e.g., 7200 for 2 hours).

#### B. Disable Auto-Cleanup (for testing)
Comment out the cleanup call in `recommend_chat_init()`:

```python
@student_bp.post('/recommend/chat/init')
@jwt_required(optional=True)
def recommend_chat_init():
    # _cleanup_old_sessions()  # Disabled for testing
    # ...
```

**⚠️ Warning**: This can cause memory leaks in production!

---

### 5. Chat Not Responding to Messages

**Symptoms:**
- Send message
- Loading spinner appears
- No response or error

**Solutions:**

#### A. Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Send a message
4. Look for the request to `/recommend/chat/message`
5. Check the response:
   - **200 OK**: Message processed successfully
   - **400 Bad Request**: Invalid session or empty message
   - **401 Unauthorized**: Token expired or invalid
   - **500 Internal Server Error**: Backend error (check logs)

#### B. Check Backend Logs
Look for error messages:
```
❌ Error in recommend_chat_message: [error details]
```

Common errors:
- **OpenAI API Error**: API key invalid or quota exceeded
- **Database Error**: Connection issues
- **JSON Parsing Error**: Malformed request

#### C. Test API Directly
Use this test script:

```python
import requests

token = "your-jwt-token-here"
session_id = "your-session-id-here"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "sessionId": session_id,
    "message": "Hello test"
}

res = requests.post(
    "http://localhost:5000/api/student/recommend/chat/message",
    json=data,
    headers=headers
)

print(f"Status: {res.status_code}")
print(f"Response: {res.json()}")
```

---

## Quick Debug Checklist

When troubleshooting chat issues, check these in order:

- [ ] **Frontend Console**: Any JavaScript errors?
- [ ] **Backend Logs**: Any Python errors?
- [ ] **Network Tab**: Is the request reaching the server?
- [ ] **Session ID**: Is the frontend using the correct session ID?
- [ ] **Active Sessions**: Does the session exist in backend memory?
- [ ] **JWT Token**: Is the token valid and not expired?
- [ ] **localStorage**: Is the state being saved/loaded correctly?
- [ ] **API Endpoints**: Are all endpoints responding correctly?

---

## Useful Commands

### Check Python Dependencies
```powershell
cd backend
pip list | Select-String "openai|flask|jwt"
```

### Test Backend Endpoints
```powershell
cd backend
python test_chat_session_flow.py
```

### Clear All State (Full Reset)
```javascript
// In browser console
localStorage.clear()
sessionStorage.clear()
location.reload()
```

### Check Backend Health
```powershell
curl http://localhost:5000/api/health
```

---

## Contact & Support

If you're still experiencing issues after trying these solutions:

1. **Collect Debug Information**:
   - Browser console logs
   - Backend terminal logs
   - Network tab request/response details
   - Steps to reproduce the issue

2. **Check Documentation**:
   - `FIX_SESSION_ERROR_AFTER_CLEAR.md`
   - `README_START_HERE.md`
   - `COMPLETE_SETUP_GUIDE.md`

3. **Test with Fresh State**:
   - Clear localStorage
   - Restart backend
   - Login again
   - Test from scratch

---

## Prevention Tips

To avoid session issues in the future:

✅ Always check browser console for errors
✅ Monitor backend logs during development
✅ Test clear functionality after code changes
✅ Use the provided test scripts regularly
✅ Keep session timeout reasonable (not too short)
✅ Handle session expiry gracefully in frontend
✅ Add proper error handling in all API calls

---

**Last Updated**: 2024
**Version**: 1.0
