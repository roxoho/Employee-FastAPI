# Employee-FastAPI


## Video Example
https://youtu.be/yUTVgjbC4qc

## Setup Instructions

1. **Database Configuration**
   - Create a cluster on MongoDB Cloud and add the connection URI to a `.env` file, or
   - Replace the URI with `mongodb://localhost` if using MongoDB locally

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Application**
   ```bash
   uvicorn main:app --reload
   ```

4. **Test the API**
   - Navigate to http://127.0.0.1:8000/docs to explore the API endpoints
