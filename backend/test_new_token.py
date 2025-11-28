#!/usr/bin/env python3
"""Test JWT token structure after changes."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from flask_jwt_extended import decode_token

app = create_app()

# Test 1: Create token via Auth.register
print("="*80)
print("TEST 1: Register endpoint token structure")
print("="*80)

with app.test_client() as client:
    resp = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123',
        'full_name': 'Test User',
        'role': 'student'
    })
    
    if resp.status_code == 201:
        data = resp.get_json()
        token = data.get('access_token')
        print(f"✅ Token created: {token[:50]}...")
        
        # Decode to see structure
        with app.app_context():
            decoded = decode_token(token)
            print(f"✅ Decoded token:")
            print(f"   - sub (identity): {decoded.get('sub')} (type: {type(decoded.get('sub')).__name__})")
            print(f"   - role (claim): {decoded.get('role')} (type: {type(decoded.get('role')).__name__})")
            print(f"   - iat: {decoded.get('iat')}")
            print(f"   - exp: {decoded.get('exp')}")
    else:
        print(f"❌ Register failed: {resp.status_code}")
        print(f"   {resp.get_json()}")

# Test 2: Try to use token in /api/student/register
print("\n" + "="*80)
print("TEST 2: Use token in /api/student/register")
print("="*80)

with app.test_client() as client:
    # First, register a course to exist
    with app.app_context():
        from app.models import db, Course
        from datetime import datetime
        
        # Check if course 1 exists, if not create
        course = Course.query.get(1)
        if not course:
            course = Course(
                title='Test Course',
                slug='test-course',
                description='Test',
                instructor_id=1,
                level='beginner',
                price=0,
                currency='VND',
                is_public=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(course)
            db.session.commit()
            print(f"✅ Created test course")
    
    # Register user
    resp = client.post('/api/auth/register', json={
        'email': 'student@test.com',
        'password': 'password123',
        'full_name': 'Student User',
        'role': 'student'
    })
    
    if resp.status_code == 201:
        data = resp.get_json()
        token = data.get('access_token')
        print(f"✅ Student registered with token: {token[:50]}...")
        
        # Try to register for course
        resp = client.post(
            '/api/student/register',
            json={'courseId': 1},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"\n✅ /api/student/register response: {resp.status_code}")
        print(f"   Data: {resp.get_json()}")
        
        if resp.status_code == 200:
            print(f"✅ SUCCESS! Token JWT structure is correct!")
        else:
            print(f"❌ FAILED! Status {resp.status_code}")
    else:
        print(f"❌ Registration failed: {resp.status_code}")
        print(f"   {resp.get_json()}")

print("\n" + "="*80)
print("✅ Test completed!")
print("="*80)
