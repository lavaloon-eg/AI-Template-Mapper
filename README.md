# Template Mapper

A machine learning-powered tool for automatically mapping different data templates to a standardized format. Perfect for handling various data sources with different column names.

## Features

- Automatic column name mapping using ML techniques
- REST API for easy integration
- Support for multiple languages (including Arabic)
- Model persistence and management
- Incremental training support
- Handles partial and complete data mapping

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/lavaloon-eg/AI-Template-Mapper.git
cd AI-Template-Mapper
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## Running the API Server

Start the server using uvicorn:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Usage

### 1. Create a New Model

```python
import requests

# Create model
response = requests.post(
    "http://localhost:8000/models",
    json={
        "standard_template": [
            "CUSTOMER_NUMBER",
            "ACC_NO",
            "Case",
            "Customer_Name",
            "BKT_IS",
            "BKT_Was"
        ],
        "examples": [
            {
                "Act RIM": "CUSTOMER_NUMBER",
                "APPLICATION ID": "ACC_NO",
                "Case": "Case",
                "CUST NAME": "Customer_Name",
                "Is": "BKT_IS",
                "Was": "BKT_Was"
            }
        ],
        "model_name": "collection_mapper"
    }
)
print(response.json())
```

### 2. Train Existing Model

```python
# Add training examples
response = requests.post(
    "http://localhost:8000/models/collection_mapper/train",
    json={
        "examples": [
            {
                "Account Rim": "CUSTOMER_NUMBER",
                "Account Number": "ACC_NO",
                "Case ID": "Case",
                "Customer Full Name": "Customer_Name",
                "Current Bucket": "BKT_IS",
                "Previous Bucket": "BKT_Was"
            }
        ]
    }
)
print(response.json())
```

### 3. Map New Data

```python
# Map data
response = requests.post(
    "http://localhost:8000/models/collection_mapper/map",
    json={
        "columns": [
            "RIM",
            "Card Acc",
            "Case",
            "Customer Name",
            "Is",
            "Was"
        ],
        "data": [
            {
                "RIM": "13587",
                "Card Acc": "5558899662147521EG",
                "Case": "P123",
                "Customer Name": "Ali",
                "Is": 99.99,
                "Was": 88.99
            }
        ]
    }
)
print(response.json())
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models` | POST | Create new model |
| `/models/{model_name}/train` | POST | Train existing model |
| `/models/{model_name}/map` | POST | Map data using model |
| `/models` | GET | List all models |
| `/models/{model_name}` | GET | Get model info |
| `/models/{model_name}` | DELETE | Delete model |

## Docker Deployment

1. Build the image:
```bash
docker build -t template-mapper .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 template-mapper
```

## Example Use Cases

### 1. Collection System Data
```python
# Map collection system data
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
    ]
}
response = requests.post(
    "http://localhost:8000/models/collection_mapper/map",
    json=data
)
```

### 2. Arabic Data Support
```python
# Map Arabic column names
arabic_examples = {
    "examples": [
        {
            "رقم العميل": "CUSTOMER_NUMBER",
            "رقم الحساب": "ACC_NO",
            "الحالة": "Case",
            "اسم العميل": "Customer_Name",
            "التصنيف": "BKT_IS",
            "التصنيف السابق": "BKT_Was"
        }
    ]
}
response = requests.post(
    "http://localhost:8000/models/collection_mapper/train",
    json=arabic_examples
)
```

## Production Deployment Tips

1. **Environment Variables**:
   - Create `.env` file for configuration
   - Set `MODEL_DIR` for model storage
   - Configure logging settings