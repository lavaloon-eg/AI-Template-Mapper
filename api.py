from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Any, Union
import pandas as pd
from datetime import datetime
import logging
from template_mapper import TemplateMapper
from persistence import ModelPersistence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Template Mapper API",
    description="API for mapping different data templates to a standardized format",
    version="1.0.0"
)

# Pydantic models with configuration
class BaseModelConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

class TrainingExample(BaseModelConfig):
    source_template: Dict[str, str]

class TrainingRequest(BaseModelConfig):
    standard_template: List[str]
    examples: List[Dict[str, str]]
    model_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MappingRequest(BaseModelConfig):
    columns: List[str]
    data: Optional[List[Dict[str, Any]]] = None
    threshold: Optional[float] = 0.3

class ModelInfo(BaseModelConfig):
    model_name: str
    standard_template: List[str]
    created_at: str
    last_updated: str
    training_examples: int

class MappingResponse(BaseModelConfig):
    mapping: Dict[str, str]
    unmapped_columns: List[str]
    transformed_data: Optional[List[Dict[str, Any]]] = None

# Initialize persistence (assuming you have the persistence module)

persistence = ModelPersistence()

@app.post("/models", response_model=ModelInfo)
async def create_model(request: TrainingRequest):
    """Create and train a new template mapper model"""
    try:
        # Create and train mapper
        mapper = TemplateMapper(request.standard_template)
        mapper.train_on_examples(request.examples)
        
        # Generate model name if not provided
        model_name = request.model_name or f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save model
        model_name = persistence.save_model(
            model_name=model_name,
            mapper=mapper,
            metadata=request.metadata
        )
        
        # Get saved model info
        _, metadata = persistence.load_model(model_name)
        return ModelInfo(**metadata)
        
    except Exception as e:
        logger.error(f"Error creating model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/models/{model_name}/map", response_model=MappingResponse)
async def map_template(model_name: str, request: MappingRequest):
    """Map columns using a trained model"""
    try:
        # Load model
        mapper, _ = persistence.load_model(model_name)
        
        # Get mapping
        mapping = mapper.map_template(
            input_template=request.columns,
            threshold=request.threshold
        )
        
        result = {
            "mapping": mapping,
            "unmapped_columns": list(set(request.columns) - set(mapping.keys())),
            "transformed_data": None
        }
        
        # Transform data if provided
        if request.data:
            df = pd.DataFrame(request.data)
            transformed = mapper.transform_data(df, mapping)
            result["transformed_data"] = transformed.to_dict('records')
            
        return MappingResponse(**result)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    except Exception as e:
        logger.error(f"Error mapping template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models"""
    try:
        models = persistence.list_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_name}", response_model=ModelInfo)
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        _, metadata = persistence.load_model(model_name)
        return ModelInfo(**metadata)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a model"""
    try:
        if persistence.delete_model(model_name):
            return {"message": f"Model '{model_name}' deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    except Exception as e:
        logger.error(f"Error deleting model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)