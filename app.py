import os
import json
import requests
from flask import Flask, render_template, request, jsonify

# Ensure 'data' directory and 'bots.json' file exist
def ensure_data_file():
    data_dir = "data"
    bots_file = os.path.join(data_dir, "bots.json")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)  # Create 'data' directory

    if not os.path.exists(bots_file):
        with open(bots_file, 'w') as f:
            json.dump([], f)  # Initialize with an empty list

# Call the function before Flask app starts
ensure_data_file()

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
                bot = {
                    "name": row["Name"],  # Make sure this matches your actual column name
                    "url": row["URL"],  # Adjust this key to match your actual column name
                    "interval": int(row["Interval"])  # Adjust this key to match your actual column name
                }
                bots.append(bot)
            except KeyError as e:
                print(f"KeyError: Missing expected key {str(e)} in row: {row}")
        return bots
    else:
        print(f"Error fetching data from API. Status code: {response.status_code}")
        return []

# Save Bots to Baserow API
def save_bot_to_baserow(name, url, interval):
    data = {
        "Name": name,      # Ensure the field name matches the Baserow column name
        "URL": url,        # Ensure the field name matches the Baserow column name
        "Interval": interval  # Ensure the field name matches the Baserow column name
    }

    response = requests.post(BASE_URL, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        print("Bot added successfully to Baserow!")
    else:
        print(f"Failed to add bot to Baserow. Status code: {response.status_code}, Response: {response.text}")

@app.route("/", methods=["GET", "POST"])
def index():
    bots = load_bots()
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]
        interval = request.form["interval"]

        save_bot_to_baserow(name, url, interval)  # Save bot to Baserow
        return render_template("index.html", bots=bots, message="Bot added successfully!")
    
    return render_template("index.html", bots=bots)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_bot(index):
    data = request.get_json()
    if data["password"] == ADMIN_PASSWORD:
        bots = load_bots()
        if 0 <= index < len(bots):
            bots.pop(index)
            save_bots(bots)
            return jsonify({"message": "Bot deleted successfully!"}), 200
    return jsonify({"error": "Unauthorized or invalid index"}), 403

# Expose the WSGI application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# This is for Vercel
application = app
