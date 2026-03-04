from functools import wraps
import json
import string
from flask import Flask
from flask import request
import paramiko
import jsonpath_ng.ext as jp
import os

app = Flask(__name__)

IP = os.getenv("UNIFI_IP")
USER = os.getenv("UNIFI_USER")
PASS = os.getenv("UNIFI_PASSWORD")
AUTH = os.getenv("SMS_AUTH")


def build_client():
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(IP, username=USER, password=PASS)
    client.exec_command("ifconfig usb0 up")
    return client


def run_command(client, command):
    _stdin, _stdout, _stderr = client.exec_command(
        f"ssh -y root@$(cat /var/run/topipv6) '/legato/systems/current/bin/cm {command}'"
    )
    return _stdout.read().decode(), _stderr.read().decode()


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            return "MISSING AUTH", 403

        auth = auth_header.split(" ", 2)
        if len(auth) != 2:
            return "INVALID AUTH", 403

        if auth[0] != "Bearer":
            return "INVALID AUTH", 403

        if auth[1] != AUTH:
            return "INVALID AUTH", 403

        return f(*args, **kwargs)

    return decorated_function


@app.route("/sms/status", methods=["GET"])
@auth_required
def sms_status():
    client = build_client()

    out_info, err_info = run_command(client, "info all")
    out_sim, err_sim = run_command(client, "sim info")

    client.close()

    data = {
        "mac": ["1C:6A:1B:7C:1F:A3"],
        "info": {},
        "sim": {},
    }

    for line in out_info.splitlines():
        key, value = line.split(":", 1)
        data["info"][key.strip()] = value.strip()

    for line in out_sim.splitlines():
        key, value = line.split(":", 1)
        data["sim"][key.strip()] = value.strip()

    out = json.dumps(data, indent=4)

    return out, 200


@app.route("/sms/retrieve", methods=["GET"])
@auth_required
def sms_retrieve():
    client = build_client()

    out_count, err_count = run_command(client, "sms count")

    client.close()

    count = out_count.replace("\n", "")
    if count == "0":
        out = "NO STORED MESSAGES"
    else:
        out_list, err_list = run_command(client, "sms list")
        out = f"{count} STORED MESSAGES:\n{out_list}"

    return out, 200


@app.route("/sms/clear", methods=["DELETE"])
@auth_required
def sms_clear():
    client = build_client()

    run_command(client, "sms clear")

    client.close()

    return "ALL STORED MESSAGES CLEARED", 200


@app.route("/sms/send/<number>", methods=["POST"])
@auth_required
def sms_send(number):
    content_path = request.args.get("path")
    if content_path:
        json_in = request.get_json(force=True)
        query = jp.parse(content_path)
        body = query.find(json_in)[0].value
    else:
        body = request.data.decode("UTF-8")

    resp = {}

    if body == "" or body is None:
        return json.dumps({"result": False, "error": "MISSING MESSAGE BODY"}), 400

    client = build_client()

    run_command(client, f'sms send {number} "{body}"')

    client.close()

    return json.dumps({"result": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8585)
