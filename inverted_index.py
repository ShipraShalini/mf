import json
import string

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.snowball import EnglishStemmer
# import jsonshelve
import shelve
from pprint import pprint

from jsonshelve import PersistentDict

filename = 'abc'
index = PersistentDict(filename='index')

db = PersistentDict(filename=filename)

# db = shelve.open(filename)

# index = shelve.open('index')



def get_stemmed_list(data):
    words_to_be_removed = string.punctuation + (set(stopwords.words('english')) - ['not'])
    stemmer = EnglishStemmer()
    words = word_tokenize(data)
    words = [w for (w not in words_to_be_removed) in words]
    return[stemmer.stem(w) for w in words]



def create_index(data):
    """
    creates inverted index
    :param string: input string
    :param id: id of the document
    :return: None
    """
    stemmed_words = get_stemmed_list(data)
    id = data['id']
    for pos, word in enumerate(stemmed_words):
        try:
            if id not in index[word]:
                index[word][id] = [pos,]
            else:
                # look for better way
                index[word][id]= list(set(index[word][id]).add(pos))
        except KeyError:
            index[word] = dict()
            index[word][id] = [pos,]

    index.sync()


def store_object(data):
    db[data['id']] = data
    create_index(data)
    db.sync()


def delete_object(oid):
    del db[oid]
    db.sync()


def get_object(oid):
    return db[oid]


def get_all():
    return json.dumps({'db':db, 'index':index})


def match(q):
    words = get_stemmed_list(q)
    id_list = list()
    for word in words:
        id_list.extend(index[word].keys())

    # assumption, verify performance
    id_list = list(set(id_list))

    object_list = list()
    for i in id_list:
        object_list.append(db[i])
    return json.dumps(object_list)

