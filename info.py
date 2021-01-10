import json


class Info:
    def __init__(self, name):
        # Open accounts data
        try:
            with open("accounts.json") as f:
                self.accounts = json.load(f)
        except FileNotFoundError:
            self.accounts = {
                "accounts": []
            }
            self.update_json()

        # Look for account to be used
        try:
            for account in self.accounts["accounts"]:
                if account["name"] == name:
                    self.account = account
            self.email = self.account["email"]
            self.password = self.account["pass"]
            self.contacts = self.account["contacts"]
        except AttributeError:
            print("New account for under profile: " + name)
            self.account = {
                "name": name,
                "email": input("Email: "),
                "pass": input("Password: "),
                "contacts": [
                    {
                        "name": input("Chat name: "),
                        "link": input("Chat link: ")
                    }
                ]
            }
            self.accounts["accounts"].append(self.account)
            self.update_json()

    def update_json(self):
        with open("accounts.json", "w") as f:
            json.dump(self.accounts, f, indent=2)

    def add_contact(self):
        self.contacts.append({
            "name": input("Chat name: "),
            "link": input("Chat link: ")
        })
