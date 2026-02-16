'''
Author: Kate Lautenbach
Assignmnet: 7, An extensible framework for natural language processing
This file holds the library for my text and the funtions that it can perform
'''
from collections import Counter, defaultdict
import random as rnd
import matplotlib.pyplot as plt
import nltk
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
import silly_text_parser as parser
import csv
from collections import Counter
from PassivePySrc import PassivePy
import re
import sankey as s
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

passivepy = PassivePy.PassivePyAnalyzer(spacy_model="en_core_web_sm")

#https://docs.python.org/3/library/re.html
# the A-Z covers uppercase, a-z covers lowercase and 0-9, roman numerals,
# and nested enumeration when followed by an uppercase so only the beginning
# of sentences and not references in the text are removed

ENUM_PATTERNS = [
    # parentheses at beginning of line
    r'(?m)^\s*\([a-z0-9ivx]+\)\s+',
    # numer dot
    r'(?m)^\s*\d+\.\s+',
    # bare letter/number
    r'(?m)^\s*\d+\s+(?=[a-z])',
    # letter dot
    r'(?m)^\s*[a-z]\.\s+',
    # d. j. text  (spaced chain)
    r'(?m)^\s*(?:[a-z]\.\s*){2,}(?=[a-z])',
    r'(?m)^\s*(?:[a-z]\.){2,}\s+(?=[a-z])',
    # roman numerals
    r'(?m)^\s*[ivx]+\.\s+']

class SillyText:

    def __init__(self):
        """ Constructor to initialize state """

        # Where all the data extracted from the loaded documents is stored
        self.data = defaultdict(dict)

    @staticmethod
    def count_clause_punctuation(text):
        '''count all commas colons, and semicolons'''
        punct = [',', ':', ';']
        clauses = 0
        for pat in punct:
            clauses += text.count(pat)
        return clauses

    @staticmethod
    def passive_voice(text):
        '''use passivepy library to '''
        result = passivepy.match_text(text)
        return int(result['passive_count'].iloc[0])


    @staticmethod
    def count_vague_terms(text):
        '''load csv with vague terms and count instances in text'''
        vague_terms = []
        with open('vagueness_lexicon.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                vague_terms.append(row[0])
        return sum(text.count(term) for term in vague_terms)

    @staticmethod
    def rid_enum(text):
        '''using the patters above this rids the fle of enumeration so numbers
        can be included and the enumerations isn't tracked'''
        for pattern in ENUM_PATTERNS:
            text = re.sub(pattern, '', text)
        return text

    @staticmethod
    def load_stop_words(words):
        '''set a variable with stop words from nltks library'''
        # A list of common or stop words. These get filtered from each file automatically
        stop_words = set(stopwords.words('english'))
        return [w for w in words if w not in stop_words]


    def pre_process(self, words):
        '''this gets rid of punctuation, stop words, unnecessary space, listing'''
        # leave nly numbers and letters
        word_clean = [word for word in words if word.isalnum()]
        # filter stop words
        filtered = self.load_stop_words(word_clean)
        return filtered


    def flex_parser(self, text, policy=False):
        """ For parsing the text and grabbing basic data """

        results = {
            'passive_count': self.passive_voice(text),
            'vague_count' : self.count_vague_terms(text),
            'clauses_count' : self.count_clause_punctuation(text),
            'numsent': len(text.split('.')),
        }
        # clean tests with preprocessor
        words = wordpunct_tokenize(text)
        words_clean = self.pre_process(words)


        results.update({'wordcount': Counter(words_clean), "numwords":len(words_clean), "avgsent": len(words_clean)/ len(text.split('.'))})

        if policy:
            add_result = parser.txt_policy_parser(text)
            results.update(add_result)
        return results


    def load_text(self, filename, label=None, policy=False):
        """ Register a text document with the framework.
         Extract and store data to be used later in our visualizations. """
        with open(filename, "r") as file:
            text = file.read()

        text = text.lower()

        if policy is True:
            # rid file of enumeration
            text = self.rid_enum(text)

        # get rid of line breaks
        text = text.replace('\n', ' ')

        results = self.flex_parser(text, policy=policy)

        # Use filename for the label if none is provided
        if label is None:
            label = filename

        for k, v in results.items():  # iterate through keys and vals
            # fill in nested dictionary of {keys : {labels:v}}
            self.data[k][label] = v

    def normalize_data(self, policy=False):
       '''make all the data for passivity, exception phrasing, numwords and
       cluase puntuation count, comparable by calculating the percentages'''

       metrics_to_normalize = ['passive_count', 'vague_count', 'exceptions', 'clauses_count', 'avgsent']

       if policy is True:
           metrics_to_normalize.append('exceptions')

       for metric in metrics_to_normalize:
           # instances total across all texts
           total = sum(self.data[metric].values())

           # create new key
           normalized_metric = f'{metric}_percentage'
           self.data[normalized_metric] = {}

           # Calculate each text's percentage of the total
           for text_label, value in self.data[metric].items():
               if total > 0:
                   self.data[normalized_metric][text_label] = (value / total) * 100
               else:
                   self.data[normalized_metric][text_label] = 0

    def wordcount_sankey(self, k=5):
        # Map each text to words using a Sankey diagram, where the thickness of the line
        # is the number of times that word occurs in the text. Users can specify a particular
        # set of words, or the words can be the union of the k most common words across
        # each text file (excluding stop words).

        # Combine counts for sankey!
        all_words = Counter()
        for text_label, word_counter in self.data['wordcount'].items():
            all_words.update(word_counter)
        word_list = [word for word, count in all_words.most_common(k)]

        # put data into dict
        sankey_data = []
        for text_label, word_counter in self.data['wordcount'].items():
            for word in word_list:
                count = word_counter.get(word, 0)
                sankey_data.append({'text': text_label, 'word': word,
                    'count': count})
        # to df
        df = pd.DataFrame(sankey_data)
        s.show_sankey(df, 'text', 'word', vals='count', png='word_count.png')



    def readability_plot(self, policy = False): #color_map=):
        '''multiple bar charts determining factors for how readable the policy is'''

        # normalize data!
        self.normalize_data()

        # Get labels (text files)
        labels = list(self.data['passive_count_percentage'].keys())

        # Metrics to visualize
        metrics = ['avgsent_percentage', 'clauses_count_percentage', 'passive_count_percentage',
         ]
        metric_names = ['Avg Words/Sentence', 'Passive', 'Vague Terms']
        if policy is True:
            metrics.append('exceptions_percentage')
            metric_names.append('Exceptions')

        # Create colors for each metric and edit to size based on if it is policy or not
        base_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
                       '#95E1D3', '#F38181']
        colors = base_colors[:len(metrics)]

        # Create figure with subplots (one per text file)
        num_texts = len(labels)
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        # flatten so I can still index it despite array
        axes = axes.flatten()

        # allow for only 1 text
        if num_texts == 1:
            axes = [axes]

        # plot each file
        for idx, label in enumerate(labels):
            ax = axes[idx]

            # get values for each metric for each text
            values = []
            for metric in metrics:
                if policy is True:
                    values.append(self.data[metric][label])
                else:
                    values.append(0)

            # create bar chart
            bars = ax.bar(metric_names, values, color=colors)

            # LABEL!
            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_ylabel('Percentage of Total (%)', fontsize=10)
            ax.set_ylim(0, max(max(values), 10) * 1.1)  # Add 10% padding
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.show()

    def vagueness_heatmap(self):
        '''heat map of how vague the text is, the more vague the more red'''

        # fixed: don't mutate this list while iterating
        text_names = list(self.data['vague_count'].keys())
        vague_vals = []

        # compute vague terms per sentence for each text
        for label in text_names:
            num_sentences = self.data['numsent'][label]
            count = self.data['vague_count'][label]

            if num_sentences > 0:
                vague_vals.append(count / num_sentences)
            else:
                vague_vals.append(0)

        # now compute colors ONCE
        if max(vague_vals) > 0:
            norm = plt.Normalize(vmin=min(vague_vals), vmax=max(vague_vals))
            colors = plt.cm.YlOrRd(norm(vague_vals))
        else:
            colors = ['gray'] * len(vague_vals)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(text_names, vague_vals, color=colors)
        ax.set_xticks(range(len(text_names)))
        ax.set_xticklabels(text_names, rotation=45, ha='right')
        ax.set_ylabel("Vague Terms per Sentence")
        ax.set_title("Policy Vagueness by Text (color = severity)")

        # add colorbar with scale of range of vagueness values
        if max(vague_vals) > 0:
            sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, label="Vagueness Severity")

        plt.tight_layout()
        plt.show()

