from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()
print("=========================================")
print("Namaste! welcome toAgriBot Nepal.        ")
print("type 'exit' to close the program.        ")
print("=========================================\n")
while True:
    user_input = input("hajur (you): ")
    if user_input.lower() == "exit":
        print("\nAgriBot: Bye! Krishi ma ramro din hos!")
        break 
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Your name is AgriBot Nepal.Help farmers with crop cultivation, diseases, and pricing in clear,concise English."},
                {"role": "user", "content": user_input}
            ],
            model="openai/gpt-oss-120b",
        )
        print(f"\nAgriBot: {chat_completion.choices[0].message.content}\n")
    except Exception as e:
        print(f"An error occurred: {e}\n")