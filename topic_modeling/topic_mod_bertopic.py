from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from flair.embeddings import TransformerDocumentEmbeddings
from sklearn.feature_extraction import text
from . import all_stopwords


class Topic:
    def __init__(self, topic_num, words, weights):
        self.topic_num = topic_num
        self.words = words
        self.weights = weights


def get_topics(csv_rows):
    print("Assessing BERTopic")
    #topic_model = BERTopic()
    # Select any transformer embedding from: https://huggingface.co/models
    # GOOD! embedding_model = TransformerDocumentEmbeddings('bert-base-uncased')
    # BAD - LEADS TO OUTLIERS! embedding_model = TransformerDocumentEmbeddings('distilbert-base-uncased')
    # BAD - LEADS TO OUTLIERS! embedding_model = TransformerDocumentEmbeddings('roberta-large')
    embedding_model = TransformerDocumentEmbeddings('xlm-roberta-base')
    # Prepare custom models
    # hdbscan_model = HDBSCAN(min_cluster_size=40, metric='euclidean', cluster_selection_method='eom',
    #                         prediction_data=True)
    # umap_model = UMAP(n_neighbors=15, n_components=10, min_dist=0.0, metric='cosine')

    stop_words = text.ENGLISH_STOP_WORDS.union(all_stopwords.stopwords_list)
    vectorizer_model = CountVectorizer(ngram_range=(1, 3), stop_words=stop_words)

    #topic_model = BERTopic()
    topic_model = BERTopic(embedding_model=embedding_model,
                           vectorizer_model=vectorizer_model)
    topic_model.umap_model.random_state = 42
    topics = None
    try:
        topics, _ = topic_model.fit_transform(csv_rows)
    except ValueError:  #raised if `y` is empty.
        print("Warning: topics has size 0, probably not enough data.")
        pass

    if not topics:
        # Topics could not be generated
        return None, None, "Could not generate topics."

    i = 0
    topic_per_sentence = []
    topics_no_duplicates = []
    for t in topics:
        i = i + 1
        topic_per_sentence.append(t)
        if t not in topics_no_duplicates:
            topics_no_duplicates.append(t)

    topics_list = []
    for n in topics_no_duplicates:
        print("Topic ", n)
        words_list = []
        weights_list = []
        words = topic_model.get_topic(n)
        for word in words:
            words_list.append(word[0])
            weights_list.append(str(word[1]))
            print("Word: " + word[0] + ", " + str(word[1]))

        topic = Topic(n, words_list, weights_list)
        topics_list.append(topic)

    # Show most frequent topics
    print("Most frequent")
    print(topic_model.get_topic_freq().head())

    return topic_per_sentence, topics_list, None




