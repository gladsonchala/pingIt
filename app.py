import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
ADMIN_PASSWORD = "scorpiPingIt"

# API Token and Table ID
API_TOKEN = "QgkF5U1aamXYnwnahYpnlpjpqt7YyXjn"
TABLE_ID = "370747"
BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
}

# Load Bots from Baserow API
def load_bots():
    response = requests.get(BASE_URL + "?user_field_names=true", headers=headers)
    if response.status_code == 200:
        rows = response.json().get("results", [])
        bots = []
        for row in rows:
            try:
                interval_value = row.get("Interval")
                if interval_value is None or not isinstance(interval_value, (int, float, str)):
                    interval = 120  # Default value if not valid
                else:
                    interval = int(interval_value)

                if row.get("Name") and row.get("URL"):
                    bot = {
                        "name": row["Name"],
                        "url": row["URL"],
                        "interval": interval
                    }
                    bots.append(bot)
            except KeyError as e:
                print(f"KeyError: Missing expected key {str(e)} in row: {row}")
            except ValueError as e:
                print(f"ValueError: Could not convert 'Interval' to int in row: {row}")
        return bots
    else:
        print(f"Error fetching data from API. Status code: {response.status_code}")
        return []

# Save Bots to Baserow API
def save_bot_to_baserow(name, url, interval):
    data = {
        "Name": name,
        "URL": url,
        "Interval": interval
    }

    response = requests.post(BASE_URL, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        print("Bot added successfully to Baserow!")
    else:
        print(f"Failed to add bot to Baserow. Status code: {response.status_code}, Response: {response.text}")

@app.route("/", methods=["POST"])
def add_bot():
    # Get form data
    bot_name = request.form.get("name")  # Name of the bot
    bot_url = request.form.get("url")    # URL of the bot
    bot_interval = request.form.get("interval")  # Interval in seconds

    # Validate input before saving the bot
    if not bot_name or not bot_url or not bot_interval:
        return "Missing required fields", 400

    try:
        # Convert interval to integer and validate it
        bot_interval = int(bot_interval)
        if bot_interval <= 0:  # Check for a positive interval
            return "Interval must be a positive integer", 400
    except ValueError:
        return "Invalid interval", 400

    # Ensure that we are not adding an empty bot
    if bot_name.strip() == "" or bot_url.strip() == "":
        return "Name and URL cannot be empty", 400

    # Call the function to save the bot to Baserow
    save_bot_to_baserow(bot_name, bot_url, bot_interval)

    # After saving, redirect back to the main page (or wherever)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>", methods=["POST"])
def delete_bot(index):
    data = request.get_json()
    if data["password"] == ADMIN_PASSWORD:
        bots = load_bots()
        if 0 <= index < len(bots):
            # Logic to remove bot from Baserow would go here
            # save_bots(bots) # Implement this if needed
            return jsonify({"message": "Bot deleted successfully!"}), 200
    return jsonify({"error": "Unauthorized or invalid index"}), 403

# Expose the WSGI application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# This is for Vercel
application = app
