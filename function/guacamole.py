import os
import httpx
from fastapi import HTTPException
from fastapi.responses import JSONResponse

GUACAMOLE_URL = os.environ.get("GUACAMOLE_URL")
GUACAMOLE_ID = os.environ.get("GUACAMOLE_ID")
GUACAMOLE_PW = os.environ.get("GUACAMOLE_PW")
GUACAMOLE_DATASOURCE = os.environ.get("GUACAMOLE_DATASOURCE")
GUACAMOLE_TOKEN = None


async def get_guacamole_connections(headers: dict, params: dict):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections",
            headers=headers,
            params=params
        )
        if response.status_code == 200 and response.content:
            return response.json()
        else:
            print("Response content is empty")
            raise HTTPException(
                status_code=500, detail="Guacamole 연결 테스트에 실패했습니다."
            )


async def get_guacamole_token(url: str, id: str, pw: str) -> str:
    global GUACAMOLE_TOKEN

    headers = {"Content-Type": "application/json"}
    data = {"username": id, "password": pw}

    async def generate_token():
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(f"{url}/api/tokens", data=data)
            if 200 <= response.status_code < 300 and response.content:
                r = response.json()
                return r.get("authToken")
            else:
                print("Guacamole token response content is empty")
                raise HTTPException(
                    status_code=500, detail="Guacamole 토큰 생성에 실패했습니다."
                )

    # Token 미발급 상태라면 Generate
    if GUACAMOLE_TOKEN is None:
        GUACAMOLE_TOKEN = await generate_token()
        print(f"############ None -> Token Generate ############")

    else:
        # 현재 토큰이 None이 아니면 유효 토큰 검증
        params = {"token": GUACAMOLE_TOKEN}
        r = await get_guacamole_connections(headers, params)
        if r.get("message") == "Permission Denied.":
            GUACAMOLE_TOKEN = await generate_token()
            print(f"############ Permission Denied -> Token Generate ############")


async def create_guacamole_connection(
    instance_tag: str,
    password: str,
    ip: str,
    username: str = "Administrator",
):
    await get_guacamole_token(GUACAMOLE_URL, GUACAMOLE_ID, GUACAMOLE_PW)

    headers = {"Content-Type": "application/json"}
    params = {"token": GUACAMOLE_TOKEN}
    data = {
        "parentIdentifier": "ROOT",
        "name": instance_tag,
        "protocol": "rdp",
        "parameters": {
            "port": "3389",
            "read-only": "",
            "swap-red-blue": "",
            "cursor": "",
            "color-depth": "",
            "clipboard-encoding": "",
            "disable-copy": "",
            "disable-paste": "",
            "dest-port": "",
            "recording-exclude-output": "",
            "recording-exclude-mouse": "",
            "recording-include-keys": "",
            "create-recording-path": "",
            "enable-sftp": "",
            "sftp-port": "",
            "sftp-server-alive-interval": "",
            "enable-audio": "",
            "security": "",
            "disable-auth": "",
            "ignore-cert": "true",
            "gateway-port": "",
            "server-layout": "",
            "timezone": "",
            "console": "",
            "width": "",
            "height": "",
            "dpi": "",
            "resize-method": "",
            "console-audio": "",
            "disable-audio": "",
            "enable-audio-input": "",
            "enable-printing": "",
            "enable-drive": "",
            "create-drive-path": "",
            "enable-wallpaper": "",
            "enable-theming": "",
            "enable-font-smoothing": "",
            "enable-full-window-drag": "",
            "enable-desktop-composition": "",
            "enable-menu-animations": "",
            "disable-bitmap-caching": "",
            "disable-offscreen-caching": "",
            "disable-glyph-caching": "",
            "preconnection-id": "",
            "hostname": ip,
            "username": username,
            "password": password,
            "domain": "",
            "gateway-hostname": "",
            "gateway-username": "",
            "gateway-password": "",
            "gateway-domain": "",
            "initial-program": "",
            "client-name": "",
            "printer-name": "",
            "drive-name": "",
            "drive-path": "",
            "static-channels": "",
            "remote-app": "",
            "remote-app-dir": "",
            "remote-app-args": "",
            "preconnection-blob": "",
            "load-balance-info": "",
            "recording-path": "",
            "recording-name": "",
            "sftp-hostname": "",
            "sftp-host-key": "",
            "sftp-username": "",
            "sftp-password": "",
            "sftp-private-key": "",
            "sftp-passphrase": "",
            "sftp-root-directory": "",
            "sftp-directory": "",
        },
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
    }

    r = await get_guacamole_connections(headers, params)
    for _, value in r.items():
        if value.get("name") == instance_tag:
            raise HTTPException(
                status_code=409, detail="같은 이름의 연결이 이미 존재합니다."
            )

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections",
            headers=headers,
            params=params,
            json=data
        )
        if response.status_code == 200:
            return "연결 생성에 성공했습니다."
        else:
            raise HTTPException(status_code=500, detail="연결 생성에 실패했습니다.")


async def delete_guacamole_connection(connection_name: str):
    # Token 유효성 체크 및 생성
    await get_guacamole_token(GUACAMOLE_URL, GUACAMOLE_ID, GUACAMOLE_PW)
    headers = {"Content-Type": "application/json"}
    params = {"token": GUACAMOLE_TOKEN}

    # Connection_list에서 Connection_num찾기
    connection_num = None
    r = await get_guacamole_connections(headers, params)

    if r:
        for key, value in r.items():
            if value.get("name") == connection_name:
                connection_num = key

    if connection_num is None:
        raise HTTPException(status_code=409, detail="존재하지 않는 Connection입니다.")

    # Connection_num을 이용해 Connection 삭제

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.delete(
            f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections/{connection_num}",
            headers=headers,
            params=params
        )
        if response.status_code != 204:
            if response.content:
                print(f"Response : {response.json()}")
            else:
                print("Response content is empty")
            raise HTTPException(status_code=500, detail="연결 삭제에 실패했습니다.")
