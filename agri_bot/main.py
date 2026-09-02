from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, JSONResponse
import requests, os, base64, datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from openai import OpenAI

load_dotenv()

app = FastAPI(title="AgriBot Pro Nepal - Money Machine v3.1")

# ========= CONFIG =========
QDRANT_URL = os.getenv("QDRANT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "agri_bot_verify_123")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
KHALTI_SECRET = os.getenv("KHALTI_SECRET")
COLLECTION_NAME = "agri_knowledge"

qdrant_client = QdrantClient(url=QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Simple DB. Later we use Postgres
USER_DB = {}

# ========= CORE AI =========
def get_embedding(text: str):
    return openai_client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding

def search_qdrant(query: str):
    vector = get_embedding(query)
    result = qdrant_client.query_points(collection_name=COLLECTION_NAME, query=vector, limit=3)
    return "\n".join([hit.payload.get("text", "") for hit in result.points])

def get_weather(district: str):
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={district},Nepal&days=3"
        data = requests.get(url).json()
        forecast = data['forecast']['forecastday']
        return f"3 din ko mausham: {forecast[0]['day']['condition']['text']}, Max {forecast[0]['day']['maxtemp_c']}°C"
    except: return ""

def ai_reply(query: str, image_b64=None, context="", district=""):
    is_nepali = any('\u0900' <= c <= '\u097F' for c in query)
    lang = "Nepali ma, saral kisan ko bhasa ma. 3-4 line ma choto jawaf." if is_nepali else "in simple English. 3-4 lines."

    weather = get_weather(district)
    prompt = f"""You are AgriBot Pro Nepal. The #1 AI for Nepali farmers.
    Context from Agri Books: {context}
    Current Weather: {weather}
    District: {district}
    Question: {query}
    Instruction: Answer {lang}. If relevant, end with: 'Premium: Bazaar bhav, expert call, 24/7 alert pauna Rs 99/month Khalti garnuhos'
    """
    if image_b64:
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}]}]
        model = "gpt-4o"
    else:
        messages = [{"role": "user", "content": prompt}]
        model = "gpt-4o-mini"

    res = openai_client.chat.completions.create(model=model, messages=messages, temperature=0.2, max_tokens=300)
    return res.choices[0].message.content

# ========= MONETIZATION =========
def check_credits(phone):
    if phone not in USER_DB: USER_DB[phone] = {"credits": 5, "paid": False, "district": "Kathmandu"}
    return USER_DB[phone]["credits"] > 0 or USER_DB[phone]["paid"]

def use_credit(phone):
    if not USER_DB[phone]["paid"]: USER_DB[phone]["credits"] -= 1

def create_khalti_payment(phone):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    payload = {
        "return_url": "https://agribotpro.com/success",
        "website_url": "https://agribotpro.com",
        "amount": 9900,
        "purchase_order_id": f"agribot_{phone}_{int(datetime.datetime.now().timestamp())}",
        "purchase_order_name": "AgriBot Pro Monthly",
        "customer_info": {"name": phone, "email": "farmer@agribot.com", "phone": phone}
    }
    headers = {"Authorization": f"Key {KHALTI_SECRET}"}
    r = requests.post(url, json=payload, headers=headers).json()
    return r.get("payment_url", "Payment link error")

# ========= WHATSAPP HANDLER =========
def send_message(to: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, headers=headers, json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text[:4000]}})

def speech_to_text(media_id):
    audio_url = f"https://graph.facebook.com/v20.0/{media_id}"
    audio = requests.get(audio_url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}).content
    with open("temp.ogg", "wb") as f: f.write(audio)
    transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=open("temp.ogg", "rb"), language="ne")
    return transcript.text

# ========= WEBHOOK =========
@app.get("/webhook")
async def verify(hub_mode=Query(None), hub_verify_token=Query(None), hub_challenge=Query(None)):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
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
            send_message(phone, f"Tapai ko 5 free sawal sakiyo. Premium jaari rakhna: {pay_url}")
            return JSONResponse({"status": "payment_sent"})

        if msg["type"] == "text":
            query = msg["text"]["body"]
            if "district" in query.lower(): USER_DB[phone]["district"] = query.split()[-1]
            reply = ai_reply(query, context=context, district=district)

        elif msg["type"] == "audio":
            query = speech_to_text(msg["audio"]["id"])
            reply = "Tapai le bhanu bhayo: " + query + "\n\n" + ai_reply(query, context=context, district=district)

        elif msg["type"] == "image":
            image_bytes = requests.get(f"https://graph.facebook.com/v20.0/{msg['image']['id']}", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}).content
            image_b64 = base64.b64encode(image_bytes).decode()
            caption = msg.get("image", {}).get("caption", "yo balima ke samasya cha?")
            reply = "Photo herera bhaneko: \n" + ai_reply(caption, image_b64=image_b64, context=context, district=district)
        else:
            reply = "Maile yo type bujhina. Text, Voice, or Photo pathaunuhos."

        use_credit(phone)
        credits_left = USER_DB[phone]["credits"]
        if credits_left < 3: reply += f"\n\n_Baki {credits_left} free sawal. Premium: Rs 99/month_"
        send_message(phone, reply)

    except Exception as e:
        print("Error:", e)
    return JSONResponse({"status": "ok"})

@app.get("/")
def home():
    return {"status": "AgriBot Pro Money Machine Running 🌾💰"}