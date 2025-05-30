import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    reload = os.getenv("ENV") == "development"

    uvicorn.run(
        "chatbot.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
