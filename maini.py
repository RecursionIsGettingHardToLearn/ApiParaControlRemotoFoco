from fastapi import FastAPI, Query
from pywizlight import wizlight, PilotBuilder

#  ─── CARGAR .env ───────────────────────────────────────
load_dotenv()                              # busca y carga .env
FOCO_IP = os.getenv("WIZ_IP") or "127.0.0.1"
#                                                     │ valor por defecto si no está
foco = wizlight(FOCO_IP)  

app = FastAPI()

@app.get("/")
async def root():
    return {"mensaje": "API de control WiZ funcionando"}

@app.get("/encender")
async def encender():
    await foco.turn_on(PilotBuilder(brightness=255))
    return {"estado": "foco encendido"}

@app.get("/apagar")
async def apagar():
    await foco.turn_off()
    return {"estado": "foco apagado"}

@app.get("/brillo")
async def brillo(valor: int = Query(128, ge=10, le=255)):
    await foco.turn_on(PilotBuilder(brightness=valor))
    return {"estado": f"brillo ajustado a {valor}"}
