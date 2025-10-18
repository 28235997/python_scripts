from flask import Flask, render_template, request, jsonify
import requests
import base64
import json
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/preview", methods=["POST"])
def preview_payload():
    """Return the JSON body that would be sent, without calling the API."""
    try:
        data = request.form
        app_id = int(data["app_id"])
        account = data["account"]
        access_key = data["access_key"]
        access_key_secret = data["access_key_secret"]
        token = data.get("token", "")
        expiry = data["expiry"]

        kubeconfig = ""
        kubeconfig_file = request.files.get("kubeconfig_file")
        if kubeconfig_file and kubeconfig_file.filename:
            path = os.path.join(app.config["UPLOAD_FOLDER"], kubeconfig_file.filename)
            kubeconfig_file.save(path)
            with open(path, "r", encoding="utf-8") as f:
                kubeconfig = f.read()
            os.remove(path)
        else:
            kubeconfig = "apiVersion: v1"

        credential_dict = {
            "kubeconfig": kubeconfig,
            "access_key": access_key,
            "access_key_secret": access_key_secret,
            "token": token
        }

        credential_json = json.dumps(credential_dict)
        credential_b64 = base64.b64encode(credential_json.encode("utf-8")).decode("utf-8")

        payload = {
            "g3application": {"id": app_id},
            "account": account,
            "credential": credential_b64,
            "credentialExpiryDateAndTime": expiry
        }

        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/send", methods=["POST"])
def send_secret():
    """Actually send the POST request to the target API."""
    result = None
    success = False
    message = ""

    try:
        data = request.form
        api_url = data["api_url"]
        app_id = int(data["app_id"])
        account = data["account"]
        access_key = data["access_key"]
        access_key_secret = data["access_key_secret"]
        token = data.get("token", "")
        expiry = data["expiry"]
        bearer_token = data.get("bearer_token", "")

        kubeconfig = ""
        kubeconfig_file = request.files.get("kubeconfig_file")
        if kubeconfig_file and kubeconfig_file.filename:
            path = os.path.join(app.config["UPLOAD_FOLDER"], kubeconfig_file.filename)
            kubeconfig_file.save(path)
            with open(path, "r", encoding="utf-8") as f:
                kubeconfig = f.read()
            os.remove(path)
        else:
            kubeconfig = "apiVersion: v1"

        credential_dict = {
            "kubeconfig": kubeconfig,
            "access_key": access_key,
            "access_key_secret": access_key_secret,
            "token": token
        }

        credential_json = json.dumps(credential_dict)
        credential_b64 = base64.b64encode(credential_json.encode("utf-8")).decode("utf-8")

        payload = {
            "g3application": {"id": app_id},
            "account": account,
            "credential": credential_b64,
            "credentialExpiryDateAndTime": expiry
        }

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        response = requests.post(api_url, headers=headers, json=payload)
        result = response.text
        if response.status_code in (200, 201):
            success = True
            message = "✅ Successfully uploaded secret."
        else:
            message = f"❌ Failed (HTTP {response.status_code})"

    except Exception as e:
        result = str(e)
        message = "❌ Error occurred during API call."

    return render_template("index.html", result=result, success=success, message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
