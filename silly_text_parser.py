'''
costom parser for legal text
'''

import re
import csv




def txt_policy_parser(text):

    # get rid of line breaks
    text = text.replace('\n', ' ')


    # get exception count
    exceptions = count_exceptions(text)

    # split by sentence
    sentences = text.split('.')

    return {'exceptions': exceptions}



def count_exceptions(text):
    '''load csv with excpetion phrases and count instances in text'''
    exceptions = []
    with open('exception_phrases.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            exceptions.append(row[0])
    return sum(text.count(term) for term in exceptions)

