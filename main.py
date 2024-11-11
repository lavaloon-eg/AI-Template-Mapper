import requests
import json
from typing import List, Dict
# API base URL
BASE_URL = "http://localhost:8000"

# Create a model
def create_model():
    data = {
        "standard_template": ["CUSTOMER_NUMBER", "ACC_NO", "Case", "Customer_Name", "BKT_IS", "BKT_Was"],
        "examples": [
            {
                "Act RIM": "CUSTOMER_NUMBER",
                "APPLICATION ID": "ACC_NO",
                "Case": "Case",
                "CUST NAME": "Customer_Name",
                "Is": "BKT_IS",
                "Was": "BKT_Was"
            },
            {
                "رقم القرض": "CUSTOMER_NUMBER",
                "رقم حساب العميل": "ACC_NO",
                "Case": "Case",
                "اسم العميل": "Customer_Name",
                "BKT": "BKT_IS",
                "BKT": "BKT_Was"
            }
        ],
        "model_name": "collection_mapper"
    }
    
    response = requests.post(f"{BASE_URL}/models", json=data)
    print("Created model:", response.json())
    
# Map new data
def map_template():
    data = {
        "columns": ["RIM", "Card Acc", "Case", "Customer Name", "Is", "Was"],
        "data": [
            {
                "RIM": "13587",
                "Card Acc": "5558899662147521EG",
                "Case": "P123",
                "Customer Name": "Ali",
                "Is": 99.99,
                "Was": 88.99
            }
        ],
        "threshold": 0.3
    }
    
    response = requests.post(
        f"{BASE_URL}/models/collection_mapper/map",
        json=data
    )
    print("Mapping result:", json.dumps(response.json(), indent=2))

def train_existing_model():
    new_training_examples = [
        {
            "Account Rim": "CUSTOMER_NUMBER",
            "Account Number": "ACC_NO",
            "Case ID": "Case",
            "Customer Full Name": "Customer_Name",
            "Current Bucket": "BKT_IS",
            "Previous Bucket": "BKT_Was"
        },
        {
            "رقم الزبون": "CUSTOMER_NUMBER",
            "رقم الحساب": "ACC_NO",
            "الحالة": "Case",
            "اسم الزبون": "Customer_Name",
            "التصنيف الحالي": "BKT_IS",
            "التصنيف السابق": "BKT_Was"
        }
    ]
    response = requests.post(
        f"http://localhost:8000/models/collection_mapper/train",
        json={
            "examples": new_training_examples
        }
    )
    print(response.json())



if __name__ == "__main__":
    
    create_model()
    train_existing_model()
    map_template()