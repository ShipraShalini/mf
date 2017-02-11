from __future__ import division

import copy
import json
import math
import string
from operator import itemgetter

from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import word_tokenize

from jsonshelve import PersistentDict

filename = 'abc'
index = PersistentDict(filename='index')

db = PersistentDict(filename=filename)


def tf(word, data):
    return data.count(word) / len(data)


def idf(docs_with_the_word):
    return math.log(len(db) / docs_with_the_word)


def get_tf_key(id, key):
    return str(id) + "_" + key


def get_stemmed_list(data):
    stop_words = set(stopwords.words('english'))
    stop_words.discard('not')
    words_to_be_removed = set(string.punctuation) | stop_words
    stemmer = EnglishStemmer()
    words = word_tokenize(data)
    words = filter(lambda x: x not in words_to_be_removed, words)
    return [stemmer.stem(w) for w in words]


def create_index(data):
    """
    creates inverted index
    :param string: input string
    :param id: id of the document
    :return: None
    """
    id = data.pop('id')
    for key, value in data.items():
        stemmed_words = get_stemmed_list(value)
        for pos, word in enumerate(stemmed_words):
            try:
                if id not in index[word]:
                    index[word][id] = {key: [pos, ]}
                    _tf = tf(word, data[key])
                    index[word]['_idf'] = idf(docs_with_the_word=len(index[word]) - 2)
                    index[word]['_tf'][get_tf_key(id, key)] = tf(word, data[key])
                elif key not in index[word][id]:
                    index[word][id][key] = [pos, ]
                    index[word]['_tf'][get_tf_key(id, key)] = tf(word, data[key])
                else:
                    # look for better way
                    pos_set = set(index[word][id][key])
                    pos_set.add(pos)
                    index[word][id][key] = list(pos_set)
            except KeyError:
                index[word] = {
                    id:
                        {
                            key: [pos, ]
                        },
                    '_idf': idf(docs_with_the_word=1),
                    '_tf': {get_tf_key(id, key): tf(word, data[key])}
                }
    index.sync()


def store_object(data):
    print "type", type(data['id'])
    db[data['id']] = data
    db.sync()
    create_index(copy.deepcopy(data))
    index.sync()


def delete_object(oid):
    try:
        stemmed_words = get_stemmed_list(db[oid]['data'])
        stemmed_words += get_stemmed_list(db[oid]['title'])
    except KeyError:
        try:
            oid = int(oid)
            stemmed_words = get_stemmed_list(db[oid]['data'])
            stemmed_words += get_stemmed_list(db[oid]['title'])
        except KeyError:
            return "not done"
    stemmed_words = list(set(stemmed_words))
    del db[oid]
    for word in set(stemmed_words):
        try:
            index[word]['_idf'] = idf(docs_with_the_word=len(index[word]) - 3)
        except ZeroDivisionError:
            del index[word]
        else:
            del index[word][oid]
            try:
                del index[word]['_tf'][get_tf_key(id, 'title')]
            except KeyError:
                pass
            try:
                del index[word]['_tf'][get_tf_key(id, 'data')]
            except KeyError:
                pass
    db.sync()
    index.sync()
    return "done"


def get_object(oid):
    return db[oid]


def get_all():
    return json.dumps({'db': db, 'index': index})


def match(q):
    # pprint(index)
    # print "\n\n\n"
    words = get_stemmed_list(q)
    id_list = []
    for word in words:
        id_list.extend(index[word].keys())
        id_list.remove('_idf')
        id_list.remove('_tf')

    # assumption, verify performance
    id_list = list(set(id_list))
    id_list.sort()
    object_list = []
    for oid in id_list:
        for word in words:
            idf = index[word]['_idf'] or 1
            try:
                tf_idf = index[word]['_tf'][get_tf_key(oid, 'title')] * idf + 0.3  # more preference to title
                tf_idf_no = 1
            except KeyError:
                tf_idf = 0
                tf_idf_no = 1
            try:
                tf_idf += index[word]['_tf'][get_tf_key(oid, 'data')] * idf
                tf_idf_no += 1
            except KeyError:
                pass
            tf_idf = tf_idf / tf_idf_no
            object_list.append({'data': db[oid], 'tf_idf': tf_idf})
    sorted(object_list, key=itemgetter('tf_idf'), reverse=True)
    print "len", len(object_list)
    return json.dumps([d['data'] for d in object_list])
