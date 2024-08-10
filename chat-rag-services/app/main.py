from fastapi import FastAPI
from app.api.endpoints import chat, document, graph
from app.api.dependencies import initialize_deps
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI(lifespan=initialize_deps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(document.router, prefix="/document", tags=["document"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
