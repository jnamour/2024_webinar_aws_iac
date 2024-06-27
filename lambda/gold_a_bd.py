import json
import pymongo
import pandas as pd



def lambda_handler(event, context):
    # Connect to the MongoDB instance
    client = pymongo.MongoClient('mongodb://user1:pass1@172.31.20.113:27017/mydatabase')
    print("client.server_info(): ", client.server_info())
    
    # Access the target database
    db = client['mydatabase']
    
    # Access the target collection
    collection = db['customers']
    
    
    # Create the document to be inserted
    document = {
        'key1': 'value1',
        'key2': 'blablabla',
        'key3': 'mas blablabla',
        # Add more fields as needed
    }
        
    # Insert the document into the collection
    #result = collection.insert_one(document)
    
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Age': [24, 27, 22, 32, 29],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    }
    
    df = pd.DataFrame(data)
    print("df.to_dict(): \n", df.to_dict('tight'))
    result = collection.insert_one(df.to_dict('tight'))
    
    # Check the result
    if result.inserted_id:
        print(f"Document inserted with ID: {result.inserted_id}")
    else:
        print("Failed to insert document")

    # Close the MongoDB connection
    client.close()