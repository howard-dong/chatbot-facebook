from chatbot import ChatBot
from fbchat import FacebookChat as FB
from info import Info
import atexit

# Main file
if __name__ == '__main__':
    name = input("Enter profile name: ")
    print("Initializing...")

    # Extract account information from accounts.json file
    profile = Info(name)

    # Initialize Chat bot object
    bot = ChatBot(name)

    # Log in and connect to each account
    print("Logging In...")
    facebook_chat = FB(profile.email, profile.password, profile.contacts)
    print("All contacts connected...")

    # Ensure that the chats are closed when
    atexit.register(facebook_chat.close)

    while True:
        try:
            contact = facebook_chat.incoming_contact()
            print("Message from: ", contact.name)
            contact.send(bot.respond(contact.last_incoming()))
        except AttributeError:
            # Catch when there are no incoming messages from contacts
            pass
        else:
            while contact.incoming():
                continue
            bot.reload()
