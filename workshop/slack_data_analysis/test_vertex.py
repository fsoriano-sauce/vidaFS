import vertexai
from vertexai.generative_models import GenerativeModel
import os

project_id = "xano-fivetran-bq" # inferred from previous bq output
location = "us-central1"

try:
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.0-pro")
    response = model.generate_content("Hello, are you working?")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Error: {e}")
