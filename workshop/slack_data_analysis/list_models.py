from google.cloud import aiplatform
import os

project_id = "xano-fivetran-bq"
location = "us-central1"

aiplatform.init(project=project_id, location=location)

print("Listing models...")
try:
    models = aiplatform.Model.list()
    for model in models:
        print(f"Model: {model.display_name} ({model.resource_name})")
    
    # Also try to list publisher models if possible (though SDK might not have direct method easily accessible without preview)
    # But let's try to just print what we found.
    if not models:
        print("No custom models found.")
        
except Exception as e:
    print(f"Error listing models: {e}")
