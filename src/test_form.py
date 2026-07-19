from fastapi import FastAPI, Request, Form
from fastapi.testclient import TestClient
from typing import List

app = FastAPI()

@app.post("/test")
async def test(
    request: Request,
    bio: str = Form(""),
):
    form = await request.form()
    return {
        "names": form.getlist("seva_names[]"),
        "keys": list(form.keys()),
        "bio": bio
    }

client = TestClient(app)
res = client.post("/test", data={"bio": "test", "seva_names[]": ["A", "B"]})
print(res.json())
