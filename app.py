import os
import json
import requests
from flask import Flask, render_template, request, jsonify

# Baserow API settings
API_TOKEN = "QgkF5U1aamXYnwnahYpnlpjpqt7YyXjn"
TABLE_ID = "370747"
BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"
HEADERS = {"Authorization": f"Token {API_TOKEN}"}
ADMIN_PASSWORD = "scorpiPingIt"

app = Flask(__name__)

# Helper to check and create columns if needed (e.g., Bot Name, URL, Interval)
def ensure_columns():
    # Check existing fields in the table (GET /fields)
    fields_url = f"https://api.baserow.io/api/database/fields/table/{TABLE_ID}/"
    response = requests.get(fields_url, headers=HEADERS)
    
    if response.status_code == 200:
        existing_fields = [field['name'] for field in response.json()]
        
        # List of fields we need
        required_fields = {
            "Bot Name": "text",
            "URL": "text",
            "Interval": "number"
        }
        
        # Create missing fields
        for field_name, field_type in required_fields.items():
            if field_name not in existing_fields:
                create_field(field_name, field_type)
    else:
        print("Error fetching existing fields:", response.text)

# Create a column/field in the Baserow table
def create_field(name, field_type):
    field_creation_url = f"https://api.baserow.io/api/database/fields/table/{TABLE_ID}/"
    field_data = {
        "name": name,
        "type": field_type,
    }
    response = requests.post(field_creation_url, headers=HEADERS, json=field_data)
    if response.status_code == 200:
        print(f"Field '{name}' created successfully.")
    else:
        print(f"Error creating field '{name}':", response.text)

# Load Bots from Baserow table
def load_bots():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        rows = response.json()['results']
        return [{"name": row["Bot Name"], "url": row["URL"], "interval": row["Interval"]} for row in rows]
    else:
        print("Error loading bots:", response.text)
        return []

# Save a new bot to Baserow
def save_bot(name, url, interval):
    data = {
        "Bot Name": name,
        "URL": url,
        "Interval": int(interval)
    }
    response = requests.post(BASE_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        print("Bot saved successfully.")
    else:
        print("Error saving bot:", response.text)

# Delete a bot from Baserow
def delete_bot_by_index(index):
    # Fetch bots to get the row ID of the bot to delete
    bots = load_bots()
    if 0 <= index < len(bots):
        row_id = bots[index]["id"]  # Fetch the row ID corresponding to the bot
        delete_url = f"{BASE_URL}{row_id}/"
        response = requests.delete(delete_url, headers=HEADERS)
        if response.status_code == 204:
            print(f"Bot at index {index} deleted successfully.")
        else:
            print("Error deleting bot:", response.text)
    else:
        print("Invalid bot index.")

# Ensure columns are created before starting the Flask app
ensure_columns()

@app.route("/", methods=["GET", "POST"])
def index():
    bots = load_bots()
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]
        interval = request.form["interval"]

        save_bot(name, url, interval)
        bots = load_bots()
        return render_template("index.html", bots=bots, message="Bot added successfully!")
    
    return render_template("index.html", bots=bots)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_bot(index):
    data = request.get_json()
    if data["password"] == ADMIN_PASSWORD:
        delete_bot_by_index(index)
        return jsonify({"message": "Bot deleted successfully!"}), 200
    return jsonify({"error": "Unauthorized or invalid index"}), 403

# Expose the WSGI application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# This is for Vercel
application = app
