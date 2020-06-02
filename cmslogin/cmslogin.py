# https://support.1password.com/command-line/
# https://docs.python.org/3.7/library/subprocess.html

import json
import os
import subprocess
import sys

import pexpect

from . import cli

UUID = {"CMS_VPN": "rsfq7iycufda7m5acghwyodapq"}


def main() -> None:
    args = cli.parse_args()

    # get the 1password password
    proc_pw = subprocess.run(
        ["pwstore", "1password.com", "get", "password"],
        capture_output=True,
        text=True,
    )

    try:
        proc_pw.check_returncode()
    except subprocess.CalledProcessError:
        print(proc_pw.stderr)
        sys.exit(proc_pw.returncode)
    else:
        onepasswordpw = proc_pw.stdout
        print("we have a 1password pw")

    # log in to onepassword
    print("Signing in to onepassword...")
    child = pexpect.spawn("op signin")
    child.expect_exact(
        "Enter the password for ryan@truss.works at truss.1password.com:"
    )
    print("sending password")
    child.sendline(onepasswordpw)

    print("We are logged in!")
    # get the 1pass item
    proc_get = subprocess.run(
        ["op", "get", "item", UUID["CMS_VPN"]], capture_output=True, text=True,
    )
    try:
        item = json.loads(proc_get.stdout)
    except json.decoder.JSONDecodeError:
        print(f"Could not decode json in: {proc_get.stdout}")
        print(f"stderr: {proc_get.stderr}")
        sys.exit(1)

    try:
        fields_by_name = {
            field.get("name"): field for field in item["details"]["fields"]
        }
    except UnboundLocalError:
        print(f"Could not do the business in: {fields_by_name}")

    username = fields_by_name.get("username").get("value")
    password = fields_by_name.get("password").get("value")

    # try to log in
    os.chdir(f"{args.path}")
    print("Spawning child process")
    child = pexpect.spawn("bash ./run-cms")

    print("waiting for username prompt...")
    child.expect_exact("Username:")
    print("sending username")
    child.sendline(username)

    print("waiting for password prompt...")
    child.expect_exact("Password:")
    print("sending password")
    child.sendline(password)

    print("waiting for totp prompt...")
    child.expect_exact("Password:")  # this is really the totp
    print("fetching totp")
    totp_get = subprocess.run(
        ["op", "get", "totp", UUID["CMS_VPN"]], capture_output=True, text=True,
    )
    print("sending totp")
    child.sendline(totp_get.stdout)

    print("finished, switching to interactive")
    child.interact()
