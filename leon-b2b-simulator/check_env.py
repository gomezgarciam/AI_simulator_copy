import os
from dotenv import load_dotenv

def verify_setup():
    # Try to load .env
    env_loaded = load_dotenv(override=True)
    
    print("--- Environment Verification ---")
    print(f".env file found and loaded: {env_loaded}")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    bucket = os.getenv("INTERNAL_DOCS_BUCKET")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print(f"Project ID: {project_id}")
    print(f"Bucket: {bucket}")
    print(f"Location: {location}")
    
    if not project_id or not bucket:
        print("\n❌ ERROR: Required variables are missing. Check your .env file.")
    else:
        print("\n✅ SUCCESS: Environment variables are correctly configured.")

if __name__ == "__main__":
    verify_setup()
