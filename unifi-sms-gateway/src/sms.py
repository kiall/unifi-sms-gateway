import json
import os
import re
from datetime import datetime, timezone, timedelta
from functools import wraps

import jsonpath_ng.ext as jp
import paramiko
from flask import Flask, request
from smspdudecoder.easy import read_incoming_sms

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
    out_count, err_count = run_command(client, "sms count")

    client.close()

    data = {
        "mac": ["1C:6A:1B:7C:1F:A3"],
        "info": {},
        "sim": {},
        "sms": {"count": out_count.replace("\n", "")},
    }

    for line in out_info.splitlines():
        key, value = line.split(":", 1)
        data["info"][key.strip()] = value.strip()

    for line in out_sim.splitlines():
        key, value = line.split(":", 1)
        data["sim"][key.strip()] = value.strip()

    out = json.dumps(data, indent=4)

    return out, 200


@app.route("/sms/list", methods=["GET"])
@auth_required
def sms_list():
    client = build_client()

    out_list, err_list = run_command(client, "sms list")

    client.close()

    out = json.dumps({"messages": _parse_sms_list(out_list)}, indent=4)

    return out, 200


def _parse_sms_list(sms_list):
    messages = []

    # Split input into individual message blocks using the separator line
    blocks = re.split(r"--\[\s*(\d+)\s*\]-+", sms_list)

    # blocks[0] is anything before the first separator (usually empty)
    # Then pairs of (index, body) follow: blocks[1]=index, blocks[2]=body, ...
    for i in range(1, len(blocks), 2):
        index = int(blocks[i])
        body = blocks[i + 1] if i + 1 < len(blocks) else ""

        msg = {"index": index}
        lines = body.splitlines()

        pdu_lines = []
        in_pdu = False

        for line in lines:
            if not line.strip():
                continue

            if in_pdu:
                # PDU hex lines are indented and contain hex bytes
                if re.match(r"^\s+[0-9A-Fa-f]{2}\s", line):
                    pdu_lines.append(line.strip())
                    continue
                else:
                    msg["pdu"] = " ".join(pdu_lines)
                    in_pdu = False

            # Match lines like " Key: value" or " Key (123): value"
            match = re.match(r"^\s+(\w+)(?:\s+\(\d+\))?:\s*(.*)", line)
            if match:
                key = match.group(1).strip().lower()
                value = match.group(2).strip()

                if key == "pdu":
                    # Start of multi-line PDU block
                    in_pdu = True
                    pdu_lines = []
                else:
                    msg[key] = value

        # Flush any remaining PDU data
        if in_pdu and pdu_lines:
            msg["pdu"] = " ".join(pdu_lines)

        # Decode PDU data if present
        if "pdu" in msg:
            try:
                pdu_hex = msg["pdu"].replace(" ", "")
                decoded = read_incoming_sms(pdu_hex)
                if decoded:
                    if decoded.get("sender"):
                        msg["sender"] = decoded["sender"]
                    if decoded.get("content"):
                        msg["text"] = decoded["content"]
                    if decoded.get("date"):
                        msg["timestamp"] = decoded["date"].isoformat()
                    if decoded.get("partial") is not None:
                        msg["partial"] = decoded["partial"]
            except Exception:
                pass

        # Parse timestamp into ISO format
        if "timestamp" in msg and msg["timestamp"]:
            parsed = _parse_timestamp(msg["timestamp"])
            if parsed:
                msg["timestamp"] = parsed.isoformat()

        messages.append(msg)

    # Sort by timestamp, newest first; messages without a timestamp go last
    messages.sort(key=lambda m: m.get("timestamp", ""), reverse=True)

    return messages


def _parse_timestamp(ts):
    """Parse a GSM timestamp like '26/03/04,11:23:43+00' into a datetime."""
    # Already ISO format (from PDU decoding) — pass through
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        pass

    # GSM format: YY/MM/DD,HH:MM:SS±ZZ (offset in quarter-hours)
    match = re.match(
        r"(\d{2})/(\d{2})/(\d{2}),(\d{2}):(\d{2}):(\d{2})([+-])(\d{2})", ts
    )
    if not match:
        return None

    yy, mm, dd, hh, mi, ss, sign, tz_quarters = match.groups()
    year = 2000 + int(yy)
    offset_minutes = int(tz_quarters) * 15
    if sign == "-":
        offset_minutes = -offset_minutes

    return datetime(
        year,
        int(mm),
        int(dd),
        int(hh),
        int(mi),
        int(ss),
        tzinfo=timezone(timedelta(minutes=offset_minutes)),
    )


@app.route("/sms/clear", methods=["DELETE"])
@auth_required
def sms_clear():
    client = build_client()

    run_command(client, "sms clear")

    client.close()

    return json.dumps({"result": True}), 200


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
