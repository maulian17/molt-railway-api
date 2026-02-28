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
    
    # FILTER HEADER PENTING
    # Kita hapus 'accept-encoding' agar server tidak mengirim data terkompresi (bikin tulisan acak)
    headers = {
        k: v for k, v in request.headers.items() 
        if k.lower() not in ['host', 'accept-encoding', 'content-length']
    }
    
    body = await request.body()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=15,
                allow_redirects=True
            )
            
            # Kirim balik konten mentah dengan status code yang sama
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                # Pastikan content-type tetap application/json
                media_type="application/json"
            )

        except Exception as e:
            if attempt == max_retries - 1:
                return Response(
                    content=json.dumps({"error": "Proxy Fail", "detail": str(e)}),
                    status_code=504,
                    media_type="application/json"
                )
            time.sleep(1)