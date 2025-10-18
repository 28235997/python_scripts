```

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

```

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Secret Uploader</title>
  <style>
    body { font-family: Arial; margin: 40px; background-color: #f5f5f5; }
    .container { background-color: white; padding: 30px; border-radius: 10px; width: 520px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    input, textarea { width: 100%; padding: 8px; margin: 6px 0; border-radius: 5px; border: 1px solid #ccc; }
    button { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-right: 8px; }
    button:hover { background-color: #0056b3; }
    pre { background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }
    .result { margin-top: 20px; padding: 10px; border-radius: 5px; }
    .success { background-color: #d4edda; color: #155724; }
    .error { background-color: #f8d7da; color: #721c24; }
  </style>
</head>
<body>
  <div class="container">
    <h2>🔐 Secret Upload Form</h2>
    <form id="secretForm" method="POST" action="/send" enctype="multipart/form-data">
      <label>API URL</label>
      <input type="text" name="api_url" value="https://xxx.xxx.com/api/v1/secrets" required>

      <label>Application ID</label>
      <input type="number" name="app_id" value="0" required>

      <label>Account</label>
      <input type="text" name="account" required>

      <label>Access Key</label>
      <input type="text" name="access_key" required>

      <label>Access Key Secret</label>
      <input type="password" name="access_key_secret" required>

      <label>Kubeconfig File (.yaml or .yml)</label>
      <input type="file" name="kubeconfig_file" accept=".yaml,.yml">

      <label>Token (optional)</label>
      <input type="text" name="token">

      <label>Credential Expiry (e.g. 2025-12-31T23:59:59Z)</label>
      <input type="text" name="expiry" value="2025-12-31T23:59:59Z" required>

      <label>API Bearer Token (optional)</label>
      <input type="password" name="bearer_token">

      <button type="button" onclick="previewJson()">Preview JSON</button>
      <button type="submit">Send Secret</button>
    </form>

    <div id="preview" style="display:none; margin-top:20px;">
      <h3>🧾 JSON Preview</h3>
      <pre id="previewContent"></pre>
    </div>

    {% if result %}
    <div class="result {{ 'success' if success else 'error' }}">
      <strong>{{ message }}</strong><br>
      <pre>{{ result }}</pre>
    </div>
    {% endif %}
  </div>

  <script>
    async function previewJson() {
      const form = document.getElementById("secretForm");
      const formData = new FormData(form);
      const res = await fetch("/preview", {
        method: "POST",
        body: formData
      });
      const json = await res.json();


      document.getElementById("preview").style.display = "block";
      document.getElementById("previewContent").textContent = JSON.stringify(json, null, 2);
    }
  </script>
</body>
</html>

```
