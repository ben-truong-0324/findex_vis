from typing import List, Union
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    model_type: Union[str, List[str]] = "Default Decision Tree"