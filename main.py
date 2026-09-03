import os
import requests
import base64
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from openai import OpenAI

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
KHALTI_SECRET_KEY = os.getenv("KHALTI_SECRET_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "agribot_v3_2026")
COLLECTION_NAME = "agribot_v3_knowledge"

qdrant = QdrantClient(url=QDRANT_URL, prefer_grpc=True, check_compatibility=False)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
USER_DB = {}

app = FastAPI()

def init_qdrant():
    try: qdrant.get_collection(COLLECTION_NAME)
    except: qdrant.create_collection(collection_name=COLLECTION_NAME, vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
init_qdrant()

def search_qdrant(query: str):
    try:
        emb = openai_client.embeddings.create(input=[query], model="text-embedding-3-small").data[0].embedding
        results = qdrant.query_points(collection_name=COLLECTION_NAME, query=emb, limit=3)
        context = "\n".join([r.payload.get("text", "") for r in results.points])
        return context if context else "General agri knowledge Nepal"
    except: return "General agri knowledge Nepal"

def ai_reply(query: str, context: str, district: str):
    system_prompt = f"You are AgriBot V3 for Nepal. User from {district}. Use context: {context}. Answer simple Nepali + English mix for farmers."
    resp = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}], max_tokens=300)
    return resp.choices[0].message.content

def check_credits(phone: str):
    if phone not in USER_DB: USER_DB[phone] = {"credits": 5, "district": "Kathmandu"}
    return USER_DB[phone]["credits"] > 0
def use_credit(phone: str):
    if phone in USER_DB: USER_DB[phone]["credits"] -= 1
    return USER_DB[phone]["credits"]

def create_khalti_payment(phone: str):
    payload = {"return_url": "https://your-app.onrailway.app/", "website_url": "https://your-app.onrailway.app/", "amount": 1000, "purchase_order_id": f"agribotv3_{phone}", "purchase_order_name": "AgriBot V3 Credits"}
    headers = {"Authorization": f"Key {KHALTI_SECRET_KEY}"}
    r = requests.post("https://a.khalti.com/api/v2/epayment/initiate/", json=payload, headers=headers)
    return r.json().get("payment_url", "")

def send_message(phone: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    requests.post(url, headers=headers, json={"messaging_product": "whatsapp", "to": phone, "text": {"body": text}})

def speech_to_text(media_id: str):
    audio_url = f"https://graph.facebook.com/v20.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    meta = requests.get(audio_url, headers=headers).json()
    audio = requests.get(meta.get("url"), headers=headers)
    with open("temp.ogg", "wb") as f: f.write(audio.content)
    return openai_client.audio.transcriptions.create(model="whisper-1", file=open("temp.ogg", "rb")).text

@app.get("/webhook")
async def verify(hub_mode=Query(None), hub_verify_token=Query(None), hub_challenge=Query(None)):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN: return PlainTextResponse(hub_challenge)
    return PlainTextResponse("Fail", 403)

@app.post("/webhook")
async def receive(request: Request):
    data = await request.json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = msg["from"]
        district = USER_DB.get(phone, {}).get("district", "Kathmandu")
        context = search_qdrant("general agri norms nepal")
        if not check_credits(phone):
            pay_url = create_khalti_payment(phone)
            send_message(phone, f"AgriBot V3: Tapai ko 5 free sawal sakiyo. Premium: {pay_url}")
            return JSONResponse({"status": "payment_sent"})
        if msg["type"] == "text":
            query = msg["text"]["body"]
            if "district" in query.lower(): USER_DB[phone]["district"] = query.split()[-1]
            reply = ai_reply(query, context, district)
            use_credit(phone)
        elif msg["type"] == "audio":
            query = speech_to_text(msg["audio"]["id"])
            reply = "Tapai le bhanu bhayo: " + query + "\n\n" + ai_reply(query, context, district)
            use_credit(phone)
        elif msg["type"] == "image":
            image_id = msg["image"]["id"]
            url = f"https://graph.facebook.com/v20.0/{image_id}"
            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            image_meta = requests.get(url, headers=headers).json()
            image_bytes = requests.get(image_meta["url"], headers=headers).content
            image_b64 = base64.b64encode(image_bytes).decode()
            vision_resp = openai_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "This is a crop image from Nepal. Diagnose disease in Nepali."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}]}])
            reply = vision_resp.choices[0].message.content
            use_credit(phone)
        else: reply = "AgriBot V3: Text, Audio, Image matra pathaunu hola."
        credits_left = USER_DB[phone]["credits"]
        if credits_left < 3: reply += f"\n\nBaki {credits_left} free sawal baaki cha"
        send_message(phone, reply)
    except Exception as e: print("Error:", e)
    return JSONResponse({"status": "ok"})

@app.get("/")
def home(): return {"status": "AgriBot V3 Pro Money Machine Running 💰🌾"}