from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SentinelPay", version="0.1.0")

# CORS (open for now, can be restricted later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check
@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "SentinelPay"
    }

# Startup & Shutdown events
@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass


# Router registration (import-safe, but debuggable)
def include_router_safely(module_path: str, prefix: str):
    try:
        module = __import__(module_path, fromlist=["router"])
        app.include_router(module.router, prefix=prefix)
    except Exception as e:
        print(f"[Router Load Failed] {module_path}: {e}")


include_router_safely("app.api.transaction", "/transaction")
include_router_safely("app.api.risk", "/risk")
include_router_safely("app.api.limit", "/limit")
include_router_safely("app.api.credit", "/credit")
