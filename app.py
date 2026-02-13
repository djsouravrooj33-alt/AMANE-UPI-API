import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ========= CONFIG =========
UPI_REGEX = re.compile(r"^[\w.\-]{2,256}@[a-zA-Z]{2,64}$")

UPI_BANK_IFSC = {
    "oksbi": ("State Bank of India", "SBIN0000001"),
    "okhdfcbank": ("HDFC Bank", "HDFC0000001"),
    "okicici": ("ICICI Bank", "ICIC0000001"),
    "okaxis": ("Axis Bank", "UTIB0000001"),
    "ybl": ("Yes Bank", "YESB0000001"),
    "paytm": ("Paytm Payments Bank", "PYTM0000001"),
}

# ========= IFSC LOOKUP =========
def get_ifsc_info(ifsc):
    try:
        r = requests.get(f"https://ifsc.razorpay.com/{ifsc}", timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ========= API =========
@app.route("/api/upi", methods=["GET"])
def upi_api():
    upi = request.args.get("upi", "").lower()

    if not UPI_REGEX.match(upi):
        return jsonify({
            "success": False,
            "error": "Invalid UPI format"
        }), 400

    handle = upi.split("@")[1]

    if handle not in UPI_BANK_IFSC:
        return jsonify({
            "success": False,
            "error": "Unknown UPI handle"
        }), 404

    bank, ifsc = UPI_BANK_IFSC[handle]
    info = get_ifsc_info(ifsc)

    response = {
        "success": True,
        "upi": upi,
        "bank": bank,
        "ifsc": ifsc
    }

    if info:
        response.update({
            "branch": info.get("BRANCH"),
            "city": info.get("CITY"),
            "state": info.get("STATE")
        })

    return jsonify(response)

@app.route("/", methods=["GET"])
def health():
    return "UPI API running"
