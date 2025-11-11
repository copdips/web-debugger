from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import io, contextlib, traceback

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
  <head><title>Python Web REPL</title></head>
  <body style="background:black;color:lime;font-family:monospace;">
    <pre id="term" style="padding:10px;height:85vh;overflow:auto;"></pre>
    <input id="cmd" style="width:100%;background:black;color:lime;font-family:monospace;" placeholder=">>> ">
    <script>
      const protocol = location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(protocol + "://" + location.host + "/ws");
      const term = document.getElementById("term");
      const cmd = document.getElementById("cmd");

      ws.onopen = () => term.textContent += "🐍 Python REPL ready\\n>>> ";
      ws.onmessage = e => {
        term.textContent += e.data + "\\n>>> ";
        term.scrollTop = term.scrollHeight;
      };
      ws.onclose = () => term.textContent += "\\n❌ Disconnected";
      cmd.addEventListener("keydown", e => {
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
async def index():
    return HTMLResponse(html)
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    namespace = {}
    await ws.send_text("Python REPL ready. Type Python code below.")
    try:
        while True:
            code = await ws.receive_text()
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    result = eval(code, namespace)
                    if result is not None:
                        print(repr(result))
            except SyntaxError:
                with contextlib.redirect_stdout(buf):
                    exec(code, namespace)
            except Exception:
                traceback.print_exc(file=buf)
            await ws.send_text(buf.getvalue())
    except WebSocketDisconnect:
        print("❌ WebSocket client disconnected.")
    except Exception as e:
        # Only send errors if the socket is still open
        try:
            await ws.send_text(f"Error: {e}")
        except RuntimeError:
            pass
    finally:
        try:
            await ws.close()
        except RuntimeError:
            pass

