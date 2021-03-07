# Keep Mega Accounts Active
# mega deletes inactive accounts
# reads credentials from a file called accounts.csv
# run this once a month to be safe (you'll forget so setup a systemd timer or cron)

import subprocess

def main():
    with open("accounts.txt") as f:
        
        for line in f.readlines():
            temp = line.split(":")

            email = temp[0].strip()
            password = temp[1].strip()

            # login
            login = subprocess.run(
                [
                    "megals",
                    "-u",
                    email,
                    "-p",
                    password,
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if "/Root" in login.stdout:
                print("Logged In", email)
            else:
                print("Error", email)

if __name__ == "__main__":
    main()
