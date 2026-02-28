import time
import requests
from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

TARGET_BASE_URL = "https://cdn.moltyroyale.com"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_engine(path: str, request: Request):
    url = f"{TARGET_BASE_URL}/{path}"
    method = request.method
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    body = await request.body()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=15
            )
            
            # Coba kirim balik apa pun yang diberikan server asli
            # Kita gunakan Response manual agar tidak error saat bukan JSON
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers={k: v for k, v in resp.headers.items() if k.lower() not in ['content-encoding', 'transfer-encoding']}
            )

        except Exception as e:
            if attempt == max_retries - 1:
                return Response(
                    content=json.dumps({"error": "Molty Server Unreachable", "detail": str(e)}),
                    status_code=504,
                    media_type="application/json"
                )
            time.sleep(1)