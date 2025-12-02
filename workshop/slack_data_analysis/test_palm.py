import vertexai
from vertexai.language_models import TextGenerationModel
import os

project_id = "xano-fivetran-bq"
location = "us-central1"

try:
    vertexai.init(project=project_id, location=location)
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict("Hello, are you working?")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Error: {e}")
