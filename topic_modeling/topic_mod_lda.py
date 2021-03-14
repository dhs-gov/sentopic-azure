from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
# Import function for stemming text
from nltk.stem.porter import PorterStemmer
import re
import numpy as np
from . import all_stopwords


class KeyWeight:
    def __init__(self, key, weight):
        self.key = key
        self.weight = weight


class Topic:
    def __init__(self, topic_num, words, weights):
        self.topic_num = topic_num
        self.words = words
        self.weights = weights


def get_topics(csv_rows, num_topics):
    print("Assessing LDA topics")

    # [6]
    tokenizer = RegexpTokenizer(r'\w+')

    # Tokenizing first observation
    tokenize_obs = tokenizer.tokenize(csv_rows[1])

    # Example of tokenizing first observation
    #print('Tokenize first observation: \n%s' % tokenize_obs)

    # Load list of common stop words

    # Create English stop words list
    eng_stop = [str(word) for word in get_stop_words('english')]
    eng_stop = eng_stop + all_stopwords.stopwords_list

    # Print a few stop words
    #print('Stop words in english: \n%s' % eng_stop[1:10])

    # [7]
    # Create p_stemmer of class PorterStemmer
    p_stemmer = PorterStemmer()

    # Text data to iterate over
    text_data = [line for line in csv_rows if line != '']

    # Convert text data into a list of comments after stop words and stemming are accounted for
    for line in range(len(csv_rows)):
        # Convert comment all to lower case
        raw_lower = text_data[line].lower()

        # Tokenize comment
        line_token = tokenizer.tokenize(raw_lower)

        # Only keep letters in comments
        clean_token = [re.sub(r'[^a-zA-Z]', '', word) for word in line_token]

        # Take out stop words
        stop_token = [word for word in clean_token if not word in eng_stop if word != '']

        # Take out stem words
        stem_token = [str(p_stemmer.stem(word)) for word in stop_token]

        # Replace comment with cleaned list of words
        text_data[line] = stop_token

    # [8]
    #  if words != ''
    words_list = [words for sublist in text_data for words in sublist]

    # Vocabulary is the set of unique words used
    vocab_total = set(words_list)

    # Take a look at few words
    #print('Few words from vocabulary list: \n%s' % list(vocab_total)[1:7])

    # Size of vocabulary list
    #print('Number of unique words in data: \n%s' % len(vocab_total))

    # [9]
    # Convert each comment into a vector by replacing the words by their unique ID
    text_ID = []

    # Loop over cleaned text data
    for line in range(len(text_data)):
        # Append comment replaced by unique word IDs
        comment_vector = [list(vocab_total).index(words) for words in text_data[line]]
        text_ID.append(comment_vector)

    # Let's check the first comment
    #print("The first comment (after processing) is: \n%s" % text_data[0])
    #print('First comment as a vector of word IDs is: \n%s' % text_ID[0])

    # [10]
    # Initialize hyperparameters in LDA

    # Dirichlet parameters
    # Alpha is the parameter for the prior topic distribution within documents
    alpha = 0.2

    # Beta is the parameter for the prior topic distribution within documents
    beta = 0.001

    # Text corpus iterations
    corpus_iterations = 200

    # Number of topics
    K = num_topics

    # Vocabulary size
    V = len(vocab_total)

    # Number of Documents
    D = len(text_ID)

    # For practical implementation, we will generate the following three count matrices:
    # 1) Word-Topic count matrix, 2) Topic-Document assignment matrix, 3) Document-Topic count matrix

    # Initialize word-topic count matrix (size K x V, K = # topics, V = # vocabulary)
    word_topic_count = np.zeros((K, V))

    # Initialize topic-document assignment matrix
    topic_doc_assign = [np.zeros(len(sublist)) for sublist in text_ID]

    # Initialize document-topic matrix
    doc_topic_count = np.zeros((D, K))

    # [11]
    # Generate word-topic count matrix with randomly assigned topics

    # Loop over documents
    for doc in range(D):

        # Loop over words in given document
        for word in range(len(text_ID[doc])):
            # Step 1: Randomly assign topics to each word in document
            # Note random.choice generates number {0,...,K-1}
            topic_doc_assign[doc][word] = np.random.choice(K, 1)

            # Record word-topic and word-ID
            word_topic = int(topic_doc_assign[doc][word])
            word_doc_ID = text_ID[doc][word]

            # Increment word-topic count matrix
            word_topic_count[word_topic][word_doc_ID] += 1

    # Print word-topic matrix
    #print('Word-topic count matrix with random topic assignment: \n%s' % word_topic_count)

    # Generate document-topic count matrix with randomly assigned topics

    # Loop over documents (D = numb. docs)
    for doc in range(D):

        # Loop over topics (K = numb. topics)
        for topic in range(K):
            # topic-document vector
            topic_doc_vector = topic_doc_assign[doc]

            # Update document-topic count
            doc_topic_count[doc][topic] = sum(topic_doc_vector == topic)

    # Print document-topic matrix
    #print('Subset of document-topic count matrix with random topic assignment: \n%s' % doc_topic_count[0:5])

    # Main part of LDA algorithm (takes a few minutes to run)
    # Run through text corpus multiple times
    for i in range(corpus_iterations):

        # Loop over all documents
        for doc in range(D):

            # Loop over words in given document
            for word in range(len(text_ID[doc])):
                # Initial topic-word assignment
                init_topic_assign = int(topic_doc_assign[doc][word])

                # Initial word ID of word
                word_id = text_ID[doc][word]

                # Before finding posterior probabilities, remove current word from count matrixes
                doc_topic_count[doc][init_topic_assign] -= 1
                word_topic_count[init_topic_assign][word_id] -= 1

    # [14]

    # Find probability used for reassigning topics to words within documents

    # Denominator in first term (Numb. of words in doc + numb. topics * alpha)
    denom1 = sum(doc_topic_count[doc]) + K * alpha

    # Denominator in second term (Numb. of words in topic + numb. words in vocab * beta)
    denom2 = np.sum(word_topic_count, axis=1) + V * beta

    # Numerators, number of words assigned to a topic + prior dirichlet param
    numerator1 = [doc_topic_count[doc][col] for col in range(K)]
    numerator1 = np.array(numerator1) + alpha
    numerator2 = [word_topic_count[row][word_id] for row in range(K)]
    numerator2 = np.array(numerator2) + beta

    # Compute conditional probability of assigning each topic
    # Recall that this is obtained from gibbs sampling
    prob_topics = (numerator1 / denom1) * (numerator2 / denom2)
    prob_topics = prob_topics / sum(prob_topics)

    # Update topic assignment (topic can be drawn with prob. found above)
    update_topic_assign = np.random.choice(K, 1, list(prob_topics))
    topic_doc_assign[doc][word] = update_topic_assign

    # Add in current word back into count matrixes
    doc_topic_count[doc][init_topic_assign] += 1
    word_topic_count[init_topic_assign][word_id] += 1

    # Compute posterior mean of document-topic distribution
    theta = (doc_topic_count + alpha)
    theta_row_sum = np.sum(theta, axis=1)
    theta = theta / theta_row_sum.reshape((D, 1))

    # Print topic distributions per sentence:
    topic_per_sentence = []
    for i in range(len(csv_rows)):
        #print(csv_rows[i])
        #print(theta[i])
        topic_weight_list = theta[i].tolist()
        # Get index of largest value in list:
        topic_index = topic_weight_list.index(max(topic_weight_list))
        #print("Topic Index: ", topic_index)
        topic_per_sentence.append(topic_index)

    if not topic_per_sentence:
        return None, None, "No LDA topics per sentence generated."

    #print("---------------------------------------------")

    # Print document-topic mixture
    #print('Subset of document-topic mixture matrix: \n%s' % theta[0:3])

    # Spam comment
    #print('Comment is 95 perc. topic 1, and 5 perc. topic 2: \n%s' % theta[10])
    #print('Comment looks like its spam: \n%s' % csv_rows[10])

    # Spam comment
    #print('Comment is 92 perc. topic 1, and 8 perc. topic 2: \n%s' % theta[4])
    #print('Comment seems to be spam: \n%s' % csv_rows[4])

    #print('Comment is 8 perc. topic 1 and 92 perc. topic 2: \n%s' % theta[11])
    #print('Comment seems ligitimate: \n%s' % csv_rows[11])

    # Compute posterior mean of word-topic distribution within documents
    phi = (word_topic_count + beta)
    phi_row_sum = np.sum(phi, axis=1)
    phi = phi / phi_row_sum.reshape((K, 1))

    # Print topic-word mixture
    #print('Topic-word mixture matrix: \n%s' % phi)

    # Explore the top words that make up each topic

    # Initialize list of dictionaries
    list_dict_topics = []

    # Loop over topics
    for topic in range(K):

        # Initialize (vocab,prob) dictionary
        mydict = {}

        # Loop over vocabular
        for word in range(V):
            # Create dictionary {(vocab,prob)}
            mydict[list(vocab_total)[word]] = phi[topic][word]

        # Create list of dictionaries
        list_dict_topics.append(mydict)

    if not list_dict_topics:
        return None, None, "No LDA list dict topics."

    # Get topic for each sentence
    i = 0
    topics = []
    for l in list_dict_topics:
        print("TOPIC ", i)
        key_weight_list = []
        for (key, value) in l.items():
            words_list.append(key)
            key_weight = KeyWeight(key, value)
            key_weight_list.append(key_weight)

        if not key_weight_list:
            return None, None, "No LDA key weight list generated."
            
        # SORT by weight!
        key_weight_list.sort(key=lambda k: k.weight, reverse=True)

        key_list = []
        weight_list = []
        max_words_per_topic = 10
        for k in range(0, max_words_per_topic):
            #print("k: ", k)
            key_list.append(key_weight_list[k].key)
            scrubbed_weight = key_weight_list[k].weight.tolist()
            print("Scrubbed weight: ", scrubbed_weight)
            weight_list.append(str(scrubbed_weight))
            print("LDA key: ", key_weight_list[k].key, " value: ", str(key_weight_list[k].weight))

        topic = Topic(i, key_list, weight_list)
        i = i+1
        topics.append(topic)

    if not topics:
        return None, None, "No LDA topics generated."

    #sorted([(value, key) for (key, value) in list_dict_topics[0].items()])[::-1][10:30]

    # Second topic
    # The first 10 words are ignored, because they most overlap with topic 1
    # Commonly appearing words in topic 2
    #sorted([(value, key) for (key, value) in list_dict_topics[1].items()])[::-1][10:30]

    return topic_per_sentence, topics, None