#encoding = UTF-8
import pysrt
import nltk
import json
import geotext
import sys
from nltk.tag.stanford import StanfordNERTagger
from config import *

class TextModel(object):
    def __init__(self, source_file, save = True):
        self.tagger = StanfordNERTagger(NER_path[0], NER_path[1])
        self.source_file = source_file
        self.subs = pysrt.open(self.source_file)
        self.parsed_subs = self.parse_subs().encode("ascii", "ignore")
        #self.tagged_text = nltk.pos_tag(nltk.word_tokenize(self.parsed_subs))
        #self.nouns = self.get_words_in_class("NN")
        #self.verbs = self.get_words_in_class("VB")
        #self.sentences = self.get_sentences(self.parsed_subs)
        #self.geotext_object = geotext.GeoText(self.parsed_subs)
        #self.cities = self.geotext_object.cities
        #self.countries = self.geotext_object.country_mentions
        self.enteties = self.extract_entities()
        if save:
            self.save_self()

    def parse_subs(self):
        completeText = ""
        for i in self.subs:
            completeText += i.text + " "
        return completeText

    def get_words_in_class(self, word_class):
        words = {}
        for i in range(len(self.tagged_text)):
            self.add_to_dictionary(self.tagged_text[i], word_class, words)
        return words

    def add_to_dictionary_old(self, word, word_class, dictionary):
        if word[1] == word_class:
            if word[0] in dictionary:
                dictionary[word[0]] += 1
            else:
                dictionary[word[0]] = 1

    def add_to_dictionary(self, word, dictionary):
        if word in dictionary:
            dictionary[word] += 1
        else:
            dictionary[word] = 1

    def save_self(self):
        print self.source_file.split(".")
        file = open(self.source_file.split(".")[0] + ".json", "w")
        json.dump([self.enteties], file, sort_keys=True, indent=4)

    def get_sentences(self, text):
        sentences = nltk.sent_tokenize(text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        return sentences

    def extract_entities(self):
        enteties = {"PERSONS": {}, "LOCATIONS": {}, "ORGANIZATIONS": {}}
        tagged_text = self.tagger.tag(nltk.word_tokenize(self.parsed_subs))
        for i in range(len(tagged_text)):
            if tagged_text[i][1] == "PERSON":
                if tagged_text[i + 1][1] == "PERSON":
                    if tagged_text[i + 2][1] == "PERSON":
                        self.add_to_dictionary(tagged_text[i][0] + " " + tagged_text[i+1][0] + " " + tagged_text[i+2][0], enteties["PERSONS"])
                    else:
                        self.add_to_dictionary(tagged_text[i][0] + " " + tagged_text[i+1][0], enteties["PERSONS"])
                else:
                    self.add_to_dictionary(tagged_text[i][0], enteties["PERSONS"])
            if tagged_text[i][1] == "LOCATION":
                if tagged_text[i + 1][1] == "LOCATION":
                    self.add_to_dictionary(tagged_text[i][0] + " " + tagged_text[i+1][0], enteties["LOCATIONS"])
                else:
                    self.add_to_dictionary(tagged_text[i][0], enteties["LOCATIONS"])
            if tagged_text[i][1] == "ORGANIZATION":
                if tagged_text[i + 1][1] == "ORGANIZATION":
                    self.add_to_dictionary(tagged_text[i][0] + " " + tagged_text[i+1][0], enteties["ORGANIZATIONS"])
                else:
                    self.add_to_dictionary(tagged_text[i][0], enteties["ORGANIZATIONS"])

        print enteties
        return enteties


model = TextModel(sys.argv[1])
