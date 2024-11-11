import requests
import json

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

if __name__ == "__main__":
    create_model()
    map_template()