from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

app = FastAPI(title="FastAPI Monitoring Example")

# --- 4 Golden Signals ---
REQUEST_COUNT = Counter("request_count", "Number of requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])
ERROR_COUNT = Counter("error_count", "Number of errors", ["endpoint"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active requests in system")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    ACTIVE_REQUESTS.inc()
    method = request.method
    endpoint = request.url.path

    try:
        response = await call_next(request)
    except Exception:
        ERROR_COUNT.labels(endpoint=endpoint).inc()
        raise
    finally:
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        ACTIVE_REQUESTS.dec()

    return response

@app.get("/")
def root():
    return {"message": "OK"}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)