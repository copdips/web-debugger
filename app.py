# app.py
import asyncio
import os
import pty
import shlex
import subprocess
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
  <head><title>Mini Linux REPL</title></head>
  <body>
    <pre id="term" style="background:black;color:lime;padding:10px;height:90vh;overflow:auto;"></pre>
    <input id="cmd" style="width:100%;" placeholder="Type a shell command...">
    <script>
      const ws = new WebSocket("wss://" + location.host + "/ws");
      const term = document.getElementById("term");
      const cmd = document.getElementById("cmd");
      ws.onmessage = (e) => { term.textContent += e.data + "\\n"; term.scrollTop = term.scrollHeight; };
      cmd.addEventListener("keydown", (e) => {
        if (e.key === "Enter") { ws.send(cmd.value); cmd.value = ""; }
      });
    </script>
  </body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Mini Linux REPL ready. Type commands below.")
    while True:
        cmd = await websocket.receive_text()
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        output, _ = await proc.communicate()
        await websocket.send_text(output.decode() if output else "(no output)")

