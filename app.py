import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
  <head><title>Browser Shell</title></head>
  <body style="background:black;color:lime;font-family:monospace;">
    <pre id="term" style="padding:10px;height:85vh;overflow:auto;"></pre>
    <input id="cmd" style="width:100%;background:black;color:lime;font-family:monospace;" placeholder="Type a shell command...">
    <script>
      const protocol = location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(protocol + "://" + location.host + "/ws");
      const term = document.getElementById("term");
      const cmd = document.getElementById("cmd");
      ws.onopen = () => term.textContent += "✅ Connected to Browser Shell\\n";
      ws.onmessage = (e) => { term.textContent += e.data + "\\n"; term.scrollTop = term.scrollHeight; };
      ws.onclose = () => term.textContent += "\\n❌ Disconnected\\n";
      cmd.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && cmd.value.trim() !== "") {
          ws.send(cmd.value);
          cmd.value = "";
        }
      });
    </script>
  </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Welcome! Type Linux commands below:")
    while True:
        try:
            cmd = await ws.receive_text()
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            output, _ = await proc.communicate()
            await ws.send_text(output.decode() or "(no output)")
        except Exception as e:
            await ws.send_text(f"Error: {e}")
            break
