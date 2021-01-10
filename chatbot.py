import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy
import tflearn
import tensorflow as tf
import random
import json
import pickle

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

class ChatBot:
    stemmer = LancasterStemmer()

    # Initialize ChatBot object
    def __init__(self, name="default"):
        self.name = name
        self.path = "./data/" + name + "/"

        # Create new data directory
        try:
            os.makedirs("./data/" + name)
            self.data = {"intents": [
                {
                    "tag": "hello",
                    "patterns": ["hello"],
                    "responses": ["Hello"]
                },
                {
                    "tag": "bye",
                    "patterns": ["bye"],
                    "responses": ["Bye"]
                }
            ]}
            self.update_json()
        except OSError:
            # Store current json data into variable
            with open(self.path + "intents.json") as file:
                self.data = json.load(file)

        self.load_data = True

        self.words, self.tags, self.training, self.output = self.load()

        self.model = self.train()

    # Load data - returns data files
    def load(self):
        words = []
        tags = []
        new_words = []
        new_tags = []
        training = []
        output = []
        docs = []

        # Fill in new arrays with json data
        for intent in self.data["intents"]:
            for pattern in intent["patterns"]:
                token = nltk.word_tokenize(pattern)
                new_words.extend(token)
                docs.append([token, intent["tag"]])

            if intent["tag"] not in new_tags:
                new_tags.append(intent["tag"])

        new_words = [ChatBot.stemmer.stem(w.lower()) for w in new_words if w != "?"]  # Make all words lowercase
        new_words = sorted(list(set(new_words)))  # isolate unique words

        new_tags = sorted(new_tags)

        try:
            with open(self.path + "data.pickle", "rb") as f:
                words, tags, training, output = pickle.load(f)
        except FileNotFoundError:
            print("Data file not found, creating new one...")
            words = new_words
            tags = new_tags
            self.load_data = False
        else:
            if words != new_words or tags != new_tags:
                print("Changes detected in json file, reloading...")
                self.load_data = False
                words = new_words
                tags = new_tags
                training = []
                output = []
            else:
                print("Data file found, no changes detected...")
                try:
                    training = training.tolist()
                    output = output.tolist()
                except AttributeError:
                    pass
        finally:
            if not self.load_data:
                out_empty = [0 for _ in range(len(tags))]

                for doc in docs:
                    bag = []

                    wrds = [ChatBot.stemmer.stem(w.lower()) for w in doc[0]]

                    for w in words:
                        if w in wrds:
                            bag.append(1)
                        else:
                            bag.append(0)

                    output_row = out_empty[:]
                    output_row[tags.index(doc[1])] = 1
                    training.append(bag)
                    output.append(output_row)

                training = numpy.array(training)
                output = numpy.array(output)

                with open(self.path + "data.pickle", "wb") as f:
                    pickle.dump((words, tags, training, output), f)

        return words, tags, training, output

    # Checks for changes in data files
    def reload(self):
        self.load_data = True

        self.words, self.tags, self.training, self.output = self.load()

        self.model = self.train()

    # Writes self.data into json file
    def update_json(self):
        with open(self.path + "intents.json", "w") as file:
            json.dump(self.data, file, indent=2)

    # Trains new model and returns it
    def train(self):
        tf.compat.v1.reset_default_graph()

        net = tflearn.input_data(shape=[None, len(self.training[0])])
        net = tflearn.fully_connected(net, 16)
        net = tflearn.fully_connected(net, 16)
        net = tflearn.fully_connected(net, len(self.output[0]), activation="softmax")
        net = tflearn.regression(net)

        model = tflearn.DNN(net)

        if self.load_data:
            try:
                model.load(self.path + "model")
            except:
                model.fit(self.training, self.output, n_epoch=800, batch_size=8, show_metric=True)
        else:
            model.fit(self.training, self.output, n_epoch=800, batch_size=8, show_metric=True)

        model.save(self.path + "model")

        return model

    # Convert work into bag
    def bag_of_words(self, s):
        bag = [0 for _ in range(len(self.words))]

        s_words = nltk.word_tokenize(s)
        s_words = [ChatBot.stemmer.stem(word.lower()) for word in s_words]

        for se in s_words:
            for i, w in enumerate(self.words):
                if w == se:
                    bag[i] = 1

        return numpy.array(bag)

    # Find response
    def find_response(self, index):
        tag = self.tags[index]

        for data in self.data["intents"]:
            if data['tag'] == tag:
                return random.choice(data['responses'])

        print("ERROR FINDING MATCHING TAG")
        return ""

    # Generate new response and update json
    def new_response(self, pattern):
        print("The pattern below is not recognized, provide a new response:")
        print(pattern)
        response = input("response:")
        tag = input("tag:")

        new_tag = True
        for data in self.data["intents"]:
            if data['tag'] == tag:
                if pattern not in data["patterns"]:
                    data["patterns"].append(pattern)
                if response not in data["responses"] and response != "":
                    data["responses"].append(response)
                new_tag = False
                break

        if new_tag:
            new = {"tag": tag,
                   "patterns": [pattern],
                   "responses": [response]
                   }
            self.data['intents'].append(new)

        self.update_json()
        return response

    # Compute input
    def respond(self, incoming):
        results = self.model.predict([self.bag_of_words(incoming)])
        print(numpy.amax(results), " at tag: ", self.tags[numpy.argmax(results)])
        if numpy.amax(results) > 0.90:
            return self.find_response(numpy.argmax(results))
        else:
            return self.new_response(incoming)
