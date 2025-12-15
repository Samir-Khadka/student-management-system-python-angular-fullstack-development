#!/usr/bin/env python3
"""
MongoDB Connection Diagnostic Tool
Run this to test MongoDB connectivity
"""

import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import os

load_dotenv()

def test_local_connection():
    """Test if we can connect to localhost:27017"""
    print("\n🔍 Testing Local MongoDB Connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 27017))
        sock.close()
        
        if result == 0:
            print("✅ Local MongoDB is accessible on port 27017")
            return True
        else:
            print("❌ Cannot connect to localhost:27017")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB Connection...")
    try:
        from pymongo import MongoClient
        
        uri = os.getenv('MONGO_URI')
        print(f"📍 Connection URI: {uri}")
        
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Try to get server info
        server_info = client.server_info()
        print(f"✅ MongoDB Connection Successful!")
        print(f"📊 Server Version: {server_info.get('version', 'Unknown')}")
        
        # Try to access database
        db = client['student_management']
        collections = db.list_collection_names()
        print(f"📚 Collections: {collections if collections else 'None (empty database)'}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {str(e)}")
        return False


def test_flask_app():
    """Test Flask app creation"""
    print("\n🔍 Testing Flask App Creation...")
    try:
        from app import create_app
        
        app = create_app('development')
        print(f"✅ Flask App Created Successfully!")
        print(f"📌 Config: {app.config.get('FLASK_ENV', 'development')}")
        print(f"📌 Debug: {app.config.get('DEBUG', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Flask App Creation Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostics"""
    print("=" * 60)
    print("MongoDB & Flask Diagnostic Tool")
    print("=" * 60)
    
    results = {
        'Local Connection': test_local_connection(),
        'MongoDB': test_mongodb_connection(),
        'Flask': test_flask_app(),
    }
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Your setup is ready.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())