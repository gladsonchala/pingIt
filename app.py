import os
import json
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
ADMIN_PASSWORD = "your_admin_password_here"

# Load Bots from JSON File
def load_bots():
    with open('data/bots.json', 'r') as file:
        return json.load(file)

# Save Bots to JSON File
def save_bots(bots):
    with open('data/bots.json', 'w') as file:
        json.dump(bots, file, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    bots = load_bots()
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]
        interval = request.form["interval"]

        bots.append({"name": name, "url": url, "interval": int(interval)})
        save_bots(bots)
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
            return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(debug=True)
