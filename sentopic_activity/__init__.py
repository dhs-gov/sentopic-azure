import os
import csv
from collections import Counter
from adaptnlp import EasySequenceClassifier
from topic_modeling import topic_mod_bertopic
from topic_modeling import topic_mod_lda
from topic_modeling import all_stopwords
from sentiment_analysis import sentiment_3class, sentiment_5star
import os, psutil
import json
import jsonpickle


class Result:
    def __init__(self, result, bert_topics, lda_topics):
        self.result = result
        self.bert_topics = bert_topics
        self.lda_topics = lda_topics


class Paragraph:
    def __init__(self, text, bertopic, lda, class3, star5):
        self.text = text
        self.bertopic = bertopic
        self.lda = lda
        self.class3 = class3
        self.star5 = star5


class Topic:
    def __init__(self, topic_num, word_weight):
        self.topic_num = topic_num
        self.word_weight = word_weight

class Word:
    def __init__(self, word, weight):
        self.word = word
        self.weight = weight

# Here, 'name' is the incoming data_in payload.
def main(name: object) -> json:

    data_list = name

    # Get sentiment for each row
    classifier = EasySequenceClassifier()
    class3_sentiment_rows = sentiment_3class.assess(classifier, data_list)
    star5_sentiment_rows = sentiment_5star.assess(classifier, data_list)
    print("Memory 1: ", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

    # Get topic numbers for each row, and words per topic
    bert_sentence_topics, bert_topics, bert_error = topic_mod_bertopic.get_topics(data_list)
    print("Num bert topics: ", len(bert_topics))

    lda_sentence_topics, lda_topics, lda_error = topic_mod_lda.get_topics(data_list, 4)
    print("Num lda topics: ", len(lda_topics))

    print("Memory 2: ", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

    # Print topic distribution
    if not bert_error:
        print("BERT Topic Distribution: ", Counter(bert_sentence_topics))
    if not lda_error:
        print("LDA Topic Distribution: ", Counter(lda_sentence_topics))

    # Create results data
    results = []
    fields = ['Text', 'BERT Topic', 'LDA Topic', '3-Class Sentiment', '5-Star Sentiment']
    for i in range(len(data_list)):
        bert_topic = None
        if bert_sentence_topics:
            bert_topic = bert_sentence_topics[i]
        lda_topic = None
        if lda_sentence_topics:
            lda_topic = lda_sentence_topics[i]

        if (data_list[i]):
            paragraph = Paragraph(
                data_list[i],
                bert_topic,
                lda_topic,
                class3_sentiment_rows[i].sentiment,
                star5_sentiment_rows[i].sentiment
            )
            results.append(paragraph)

    r = Result(results, bert_topics, lda_topics)

    json_out = jsonpickle.encode(r, unpicklable=False)
    #print("JSON STR OUT: ", json_out)

    if json_out:
        return json_out
    else:
        return "Unknown error performing sentiment analysis and topic modeling."


