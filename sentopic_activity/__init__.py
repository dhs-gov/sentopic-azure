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


class Resultz:
    def __init__(self, paras, berts, ldas):
        self.paras = paras
        self.berts = berts
        self.ldas = ldas

class Res:
    def __init__(self, p, bert, lda):
        self.p
        self.bert
        self.lda

class Paragraph:
    def __init__(self, text, bertopic, lda, class3, star5):
        self.text = text
        self.bertopic = bertopic
        self.lda = lda
        self.class3 = class3
        self.star5 = star5


class Topic:
    def __init__(self, topic_num, word, weight):
        self.topic_num = topic_num
        self.word = word
        self.weight = weight





# Here, 'name' is the incoming data_in payload.
def main(name: object) -> json:

    data_list = name
    print("sent list: ", data_list)

    # Get sentiment for each row
    classifier = EasySequenceClassifier()
    class3_sentiment_rows = sentiment_3class.assess(classifier, data_list)
    star5_sentiment_rows = sentiment_5star.assess(classifier, data_list)
    print("Memory 1")
    print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

    # Get topic numbers for each row, and words per topic
    bert_sentence_topics, bert_topics = topic_mod_bertopic.get_topics(data_list)
    lda_sentences_topics, lda_topics = topic_mod_lda.get_topics(data_list, 4)
    print("Memory 2")
    print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

    # Print topic distribution
    print("BERT Topic Distribution: ", Counter(bert_sentence_topics))
    print("LDA Topic Distribution: ", Counter(lda_sentences_topics))

    
    # Create results data
    paras = []
    fields = ['Text', 'BERT Topic', 'LDA Topic', '3-Class Sentiment', '5-Star Sentiment']
    for i in range(len(data_list)):
        if (data_list[i]):
            #row_data.append(data_list[i])
            #row_data.append(bert_sentence_topics[i])
            #row_data.append(lda_sentences_topics[i])
            #row_data.append(class3_sentiment_rows[i].sentiment)
            #row_data.append(star5_sentiment_rows[i].sentiment)

            paragraph = Paragraph(
                data_list[i],
                bert_sentence_topics[i],
                lda_sentences_topics[i],
                class3_sentiment_rows[i].sentiment,
                star5_sentiment_rows[i].sentiment
            )
            paras.append(paragraph)
    
    # Create BERT topics data
    bert_topics = []
    #bert_out = filename + "_bert_topics_out.csv"
    fields = ['BERT Topic', 'Word', 'Weight']
    for i in range(len(bert_topics)):
        for j in range(len(bert_topics[i].words)):
            #row_data.append(bert_topics[i].topic_num)
            #row_data.append(bert_topics[i].words[j])
            #row_data.append(bert_topics[i].weights[j])
            topic = Topic(
                bert_topics[i].topic_num,
                bert_topics[i].words[j],
                bert_topics[i].weights[j]
            )
            bert_topics.append(topic)


    # Create BERT topics table
    #with open(bert_out, 'w', newline='', encoding='cp850', errors='ignore') as csvfile:
    #    csvwriter = csv.writer(csvfile, delimiter='^')
    #    csvwriter.writerow(fields)
    #    csvwriter.writerows(rows)


    # Create LDA topics data
    #lda_out = filename + "_lda_topics_out.csv"
    lda_topics = []
    fields = ['LDA Topic', 'Word', 'Weight']
    print("LDA size: ", )
    for i in range(len(lda_topics)):
        print("LDA i: ", i)
        for j in range(len(lda_topics[i].words)):
            #print("LDA j: ", j)
            #row_data = []
            #row_data.append(lda_topics[i].topic_num)
            #row_data.append(lda_topics[i].words[j])
            #row_data.append(lda_topics[i].weights[j])

            topic = Topic(
                lda_topics[i].topic_num,
                lda_topics[i].words[j],
                lda_topics[i].weights[j]
            )

            lda_topics.append(topic)

    # Create LDA topics table
    #with open(lda_out, 'w', newline='', encoding='cp850', errors='ignore') as csvfile:
    #    csvwriter = csv.writer(csvfile, delimiter='^')
    #    csvwriter.writerow(fields)
    #    csvwriter.writerows(rows)

   
    r = Resultz(paras, bert_topics, lda_topics)

    json_out = jsonpickle.encode(r, unpicklable=False)
    #print("JSON STR OUT: ", json_out)

    if json_out:
        return json_out
    else:
        return "Unknown error performing sentiment analysis and topic modeling."


