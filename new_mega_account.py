# fork of https://github.com/IceWreck/MegaScripts
# Create New Mega Accounts
# saves credentials to a file called accounts.csv

import requests
import subprocess
import time
import re
import random
import string
import threading

MINIMUM_PASSWORD_LENGTH = 32
ACCOUNT_TO_GENERATE = int(input("Insert how many account have i to generate: "))

def find_url(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class MegaAccount:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def register(self):
        mail_req = requests.get(
            "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en"
        ).json()
        self.email = mail_req["email_addr"]
        self.email_token = mail_req["sid_token"]

        # begin resgistration
        registration = subprocess.run(
            [
                "megareg",
                "--register",
                "--email",
                self.email,
                "--name",
                self.name,
                "--password",
                self.password,
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = registration.stdout

        rows = output.split("\n")
        self.verify_command = None
        for row in rows:
            if "megareg --verify" in row:
                self.verify_command = row
        
    def no_verify_command(self):
        return self.verify_command is None

    def verify(self):
        # check if there is mail
        mail_id = None
        for i in range(5):
            if mail_id is not None:
                break
            time.sleep(10)
            check_mail = requests.get(
                f"https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={self.email_token}"
            ).json()
            for email in check_mail["list"]:
                if "MEGA" in email["mail_subject"]:
                    mail_id = email["mail_id"]
                    break

        # get verification link
        if mail_id is None:
            return
        view_mail = requests.get(
            f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={self.email_token}"
        )
        mail_body = view_mail.json()["mail_body"]
        links = find_url(mail_body)

        self.verify_command = str(self.verify_command).replace("@LINK@", links[2])

        # perform verification
        verification = subprocess.run(
            self.verify_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        if "registered successfully!" in str(verification.stdout):
            print("Success. Account Details are:")
            details = f"{self.email} - {self.password}"
            print(details)

            # save to file
            with open("accounts.txt", "a") as f:
                f.write(details + "\n")
                f.close()
        else:
            print("Failed.")


def new_account():
    name = "".join(random.choice(string.ascii_lowercase) for x in range(12))
    password = name = "".join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for x in range(MINIMUM_PASSWORD_LENGTH))
    acc = MegaAccount(name, password)
    acc.register()
    if acc.no_verify_command():
        print("Cannot retrieve verify command, sorry")
    else:
        print("Registered. Waiting for verification email...")
        acc.verify()

if __name__ == "__main__":
    # how many accounts to create at once (keep the number under 10)
    for count in range(ACCOUNT_TO_GENERATE):
        t = threading.Thread(target=new_account)
        t.start()
