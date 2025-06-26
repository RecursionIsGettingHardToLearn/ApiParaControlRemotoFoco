from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pywizlight import wizlight, PilotBuilder
import os
from dotenv import load_dotenv
import logging

# ─── CONFIGURACIÓN ───────────────────────────────────────
load_dotenv(override=True)
#FOCO_IP = os.getenv("WIZ_IP")
FOCO_IP ="192.168.87.30"
foco = wizlight(FOCO_IP)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wiz-webhook")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rgb_map = {
    "rojo":      (255, 0,   0),
    "verde":     (0,   255, 0),
    "azul":      (0,   0, 255),
    "amarillo":  (255, 255, 0),
    "cian":      (0,   255, 255),
    "magenta":   (255, 0, 255),
    "blanco":    (255, 255, 255),
    "esmeralda": (80,  200, 120),
}

@app.post("/webhook")
async def dialogflow_webhook(request: Request):
    try:
        body = await request.json()
        action = body.get("queryResult", {}).get("action", "")

        if action == "turn_on_light":
            await foco.turn_on(PilotBuilder(brightness=255))
            fulfillment_text = "He encendido la luz."
        elif action == "turn_off_light":
            await foco.turn_off()
            fulfillment_text = "He apagado la luz."
        elif action == "set_color":
            color = body["queryResult"]["parameters"].get("color", "").lower()
            rgb = rgb_map.get(color)
            if not rgb:
                raise ValueError(f"Color desconocido: {color}")
            await foco.turn_on(PilotBuilder(rgb=rgb))
            fulfillment_text = f"He cambiado el color a {color}."
        else:
            fulfillment_text = "No entendí el comando."

        return {
            "fulfillmentText": fulfillment_text,
            "source": "wiz-fastapi"
        }

    except Exception as e:
        # Guarda stacktrace en logs para debugging
        logger.exception("Error al procesar webhook")
        # Devuelve el mensaje de error a Dialogflow
        return {
            "fulfillmentText": f"❌ Ocurrió un error: {str(e)}",
            "source": "wiz-fastapi",
            "errorDetails": repr(e)
        }
