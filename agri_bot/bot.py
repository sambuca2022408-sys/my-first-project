import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWM_API_KEY = os.getenv("OWM_API_KEY")


def get_weather(location: str):
    if not OWM_API_KEY:
        return None, "OpenWeatherMap API key not configured (OWM_API_KEY)."
    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={OWM_API_KEY}"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None, f"Weather API error: {resp.status_code} - {resp.text}"
        data = resp.json()
        result = {
            "location": f"{data.get('name')}, {data.get('sys', {}).get('country')}",
            "temp_c": data.get("main", {}).get("temp"),
            "weather": data.get("weather", [{}])[0].get("description", ""),
        }
        return result, None
    except Exception as e:
        return None, str(e)


def advice_from_weather(w):
    if not w:
        return "No weather data available."
    parts = []
    temp = w.get("temp_c")
    desc = (w.get("weather") or "").lower()
    if temp is not None:
        if temp < 10:
            parts.append("Cold: protect seedlings and apply frost safeguards.")
        elif temp < 25:
            parts.append("Mild: generally good for crops.")
        else:
            parts.append("Hot: irrigate early morning/evening and provide shade where possible.")
    if "rain" in desc:
        parts.append("Rain expected: postpone irrigation and protect harvested produce.")
    if not parts:
        return "No specific advice available."
    return "\n".join(parts)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to AgriNepal Bot — send /weather <city> to get local weather and simple farming advice."
    )


def weather_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /weather <city>")
        return
    location = " ".join(context.args)
    update.message.reply_text(f"Checking weather for {location}...")
    w, err = get_weather(location)
    if err:
        update.message.reply_text(f"Error: {err}")
        return
    msg = f"Weather for {w.get('location')}\nTemperature: {w.get('temp_c')} °C\nConditions: {w.get('weather')}\n\nAdvice:\n{advice_from_weather(w)}"
    update.message.reply_text(msg)


def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Commands:\n/start - welcome\n/weather <city> - current weather + advice\n/help - this message")


def main():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN not set. See .env.example")
        return
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("weather", weather_cmd))

    print("Starting AgriNepal Bot (polling). Press Ctrl-C to stop.")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
