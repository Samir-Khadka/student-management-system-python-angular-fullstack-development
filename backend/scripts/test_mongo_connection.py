#!/usr/bin/env python3
"""
Test MongoDB connection with different approaches
"""
import sys
import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient

from pymongo.errors import ConnectionFailure, ConfigurationError

# MongoDB Atlas credentials
USERNAME = "sushantkush70_db_user"
PASSWORD = "WiOhFQmuyAJTKUWH"
CLUSTER = "cluster0.yqpbkly.mongodb.net"
DATABASE = "student_management"

print("Testing MongoDB Atlas connections...\n")

# Test 1: SRV connection string
print("=" * 60)
print("Test 1: MongoDB Atlas SRV Connection String")
print("=" * 60)
srv_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER}/{DATABASE}?retryWrites=true&w=majority"
print(f"URI: mongodb+srv://{USERNAME}:****@{CLUSTER}/{DATABASE}")

try:
    client = MongoClient(srv_uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    print("✅ SUCCESS: Connected using SRV string!")
    print(f"   Database: {client[DATABASE].name}")
    print(f"   Collections: {client[DATABASE].list_collection_names()}")
    client.close()
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {str(e)}\n")

# Test 2: Direct connection with resolved hosts
print("\n" + "=" * 60)
print("Test 2: Direct MongoDB Connection (Standard)")
print("=" * 60)

# Common MongoDB Atlas shard naming convention
shard_hosts = [
    f"cluster0-shard-00-00.yqpbkly.mongodb.net:27017",
    f"cluster0-shard-00-01.yqpbkly.mongodb.net:27017", 
    f"cluster0-shard-00-02.yqpbkly.mongodb.net:27017"
]

direct_uri = f"mongodb://{USERNAME}:{PASSWORD}@{','.join(shard_hosts)}/{DATABASE}?ssl=true&replicaSet=atlas-lvgfnm-shard-0&authSource=admin&retryWrites=true&w=majority"
print(f"URI: mongodb://{USERNAME}:****@<shards>/{DATABASE}")

try:
    client = MongoClient(direct_uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    print("✅ SUCCESS: Connected using direct connection!")
    print(f"   Database: {client[DATABASE].name}")
    print(f"   Collections: {client[DATABASE].list_collection_names()}")
    client.close()
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {str(e)}\n")

print("\n" + "=" * 60)
print("Test 3: DNS Resolution Check")
print("=" * 60)

try:
    import dns.resolver
    print("✅ dnspython is installed")
    
    try:
        srv_records = dns.resolver.resolve(f'_mongodb._tcp.{CLUSTER}', 'SRV')
        print(f"✅ SRV records found:")
        for srv in srv_records:
            print(f"   - {srv.target}:{srv.port}")
    except Exception as e:
        print(f"❌ SRV lookup failed: {str(e)}")
        
except ImportError:
    print("❌ dnspython is not installed")

print("\n" + "=" * 60)
print("Recommendation:")
print("=" * 60)

print("""
If SRV connection fails but direct connection works:
1. Update your .env file with the direct connection string
2. The app will work with the standard mongodb:// URI

If both fail:
1. Check your internet connection
2. Verify MongoDB Atlas cluster is accessible
3. Check if your IP is whitelisted in MongoDB Atlas
4. Try accessing from MongoDB Compass to verify credentials
""")
