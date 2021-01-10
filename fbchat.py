from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


INCOMING_TEXT_PATH = """//div[@data-testid="messenger_incoming_text_row"]"""
OUTGOING_TEXT_PATH = """//div[@data-testid="outgoing_message"]"""
INCOMING_GROUP_PATH = """//div[@data-testid="incoming_group"]"""
OUTGOING_GROUP_PATH = """//div[@data-testid="outgoing_group"]"""
INPUT_BOX_PATH = """//*[@id="mount_0_0"]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/div/form/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div/div/div/div"""
MESSAGES_PATH = """//div[@aria-label="Messages"]"""
NAME_PATH = """//*[@id="mount_0_0"]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div[2]/div/div[1]/span/span"""

c_options = Options()
c_options.add_argument("--headless")
PATH = "C:\Program Files (x86)\chromedriver.exe"


class Contact:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.driver = webdriver.Chrome(PATH, options=c_options)
        self.driver.get(link)

    # Returns true if latest message is incoming
    def incoming(self):
        messages = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, MESSAGES_PATH)))
        ig = self.driver.find_elements_by_xpath(INCOMING_GROUP_PATH)
        og = self.driver.find_elements_by_xpath(OUTGOING_GROUP_PATH)
        children = messages.find_elements_by_xpath("*")
        try:
            return children.index(ig[ig.__len__() - 1]) > children.index(og[og.__len__() - 1])
        except (IndexError, ValueError):
            return False

    # Get last incoming message
    def last_incoming(self):
        incs = self.driver.find_elements_by_xpath(INCOMING_TEXT_PATH)
        return incs[incs.__len__() - 1].text

    # Get last outgoing message
    def last_outgoing(self):
        outs = self.driver.find_elements_by_xpath(OUTGOING_TEXT_PATH)
        return outs[outs.__len__() - 1].text

    # Send message to input box
    def send(self, msg):
        for m in msg.split(", "):
            inputbox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, INPUT_BOX_PATH)))
            inputbox.send_keys(m)
            inputbox.send_keys(Keys.RETURN)


class FacebookChat:
    def __init__(self, email, password, contacts):
        self.email = email
        self.password = password
        self.contacts = []
        # Fill contacts list with Contact objects
        for contact in contacts:
            c = Contact(contact["name"], contact["link"])
            email = WebDriverWait(c.driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
            email.send_keys(self.email)

            password = WebDriverWait(c.driver, 20).until(EC.presence_of_element_located((By.NAME, "pass")))
            password.send_keys(self.password)
            password.send_keys(Keys.RETURN)

            name = WebDriverWait(c.driver, 10).until(EC.presence_of_element_located((By.XPATH, NAME_PATH)))
            print("Connected to chat with: " + c.name + " (" + name.text + ")")

            self.contacts.append(c)

    # # Get recent contact
    # def recent_contact(self):
    #     contacts = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, CONTACTS_PATH)))
    #     # contacts = self.driver.find_elements_by_xpath(CONTACTS_PATH)
    #
    #     for c in range(5):
    #         print("--------")
    #         print(contacts[c].text)
    #         print("--------")

    # Get incoming contact
    def incoming_contact(self):
        for contact in self.contacts:
            if contact.incoming():
                return contact
        return None

    # Close all drivers
    def close(self):
        for c in self.contacts:
            c.driver.close()
        return
