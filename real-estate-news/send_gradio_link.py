import sys
import json
import pywhatkit as kit

# Extract the Gradio live link from the command line argument
gradio_link = sys.argv[1]

# Load the subscribers from the JSON file
with open('subscribers.json', 'r') as file:
    data = json.load(file)
    subscribers = data.get("subscribers", [])

# Send the Gradio live link to each subscriber via WhatsApp with a personalized message
for subscriber in subscribers:
    name = subscriber.get("name")
    phone_number = subscriber.get("phone_number")
    message = f"Hi {name}, here is the Gradio live link for your real estate news: {gradio_link}"
    
    try:
        kit.sendwhatmsg_instantly(phone_number, message)
        print(f"Gradio link sent to {name} ({phone_number})")
    except Exception as e:
        print(f"Failed to send message to {name} ({phone_number}): {e}")