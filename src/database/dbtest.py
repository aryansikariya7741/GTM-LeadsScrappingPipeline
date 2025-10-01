from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

# Your updated Atlas URI
uri = "mongodb+srv://Cluster25172:pass123@cluster25172.bj5nf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster25172"

# Create client with certifi CA for SSL
client = MongoClient(uri, tlsAllowInvalidCertificates=True)


# Test connection
try:
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB Atlas!")
except Exception as e:
    print("❌ Connection error:", e)
