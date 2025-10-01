from fastapi import FastAPI, HTTPException
import os
from pydantic import BaseModel, Field
from typing import Dict, Any
from pathlib import Path
import json
import bcrypt
import uvicorn


# Simple user payload schema
class AuthPayload(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=256)


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"


def ensure_data_file_exists() -> None:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump({"users": []}, f, ensure_ascii=False, indent=2)


def load_data() -> Dict[str, Any]:
    ensure_data_file_exists()
    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Reset to default if file is corrupted
            return {"users": []}


def save_data(data: Dict[str, Any]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_user(data: Dict[str, Any], username: str) -> Dict[str, Any] | None:
    for user in data.get("users", []):
        if user.get("username") == username:
            return user
    return None


app = FastAPI(title="Password Manager Demo API")


@app.post("/api/signup")
def signup(payload: AuthPayload):
    # Load current users
    data = load_data()

    # Check duplicate username
    if find_user(data, payload.username) is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password with bcrypt (never store plaintext)
    password_bytes = payload.password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    # Save new user
    data.setdefault("users", []).append(
        {"username": payload.username, "password_hash": password_hash}
    )
    save_data(data)

    return {"msg": "Signup success", "username": payload.username}


@app.post("/api/login")
def login(payload: AuthPayload):
    data = load_data()
    user = find_user(data, payload.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    stored_hash = user.get("password_hash", "")
    if not stored_hash:
        raise HTTPException(status_code=500, detail="User data invalid")

    # Verify password
    ok = bcrypt.checkpw(payload.password.encode("utf-8"), stored_hash.encode("utf-8"))
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"msg": "Login success", "username": payload.username}


if __name__ == "__main__":
    os.environ["UVICORN_RUN_MAIN"] = "true"
    os.environ["PYTHONUNBUFFERED"] = "1"
    # Run with: python backend/main.py
    # Configure via env vars when needed:
    #   HOST=127.0.0.1 PORT=9099 RELOAD=0


    # tìm host, port, reload phù hợp (không bị dùng chung với một dịch vụ khác)
    # cmd tìm host netstat -ano | findstr :9099 để xem port có bị chiếm không
    # nếu bị chiếm thì đổi port khác : 9099 -> 9090 -> 8081....
    # DÒ PORT NÀO KHÔNG BỊ CHIẾM THÌ MỚI CHẠY SERVER ĐƯỢC : netstat -ano (DÒ TẤT CẢ CÁC PORT)
    # có thể cmd tasklist | findstr 9099 để xem port đó của chương trình nào
    # hoặc Cmd netstat -aon | findstr LISTENING để xem tất cả các port đang lắng nghe
    # cmd taskkill /PID <pid> /F để tắt chương trình chiếm port
    # ví dụ: taskkill /PID 1234 /F
    
    host = os.getenv("HOST", "127.0.0.1")
    port_str = os.getenv("PORT", "9099")
    reload_str = os.getenv("RELOAD", "0")
    
    try:
        port = int(port_str)
    except ValueError:
        port = 9099
    reload_flag = reload_str in {"1", "true", "True"}

    # On some Windows setups, enabling reload can trigger socket permission errors (WinError 10013).
    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)


