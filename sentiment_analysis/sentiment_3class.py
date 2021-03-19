
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


class Sentiment:
    def __init__(self, sentiment, negative, neutral, positive):
        self.sentiment = sentiment
        self.negative = float(truncate(negative, 3))
        self.neutral = float(truncate(neutral, 3))
        self.positive = float(truncate(positive, 3))


def calc_sentiment(confidence_score):
    largest_label = 'LABEL_0'
    largest_score = 0.0

    for label in confidence_score.labels:
        #print("cf: ", label)
        if label.score > largest_score:
            largest_label = str(label)
            largest_score = label.score

    #print("largest_label: ", largest_label)
    if "LABEL_0" in largest_label:
        return "negative"
    elif "LABEL_1" in largest_label:
        return "neutral"
    elif "LABEL_2" in largest_label:
        return "positive"
    else:
        print("WARNING: unknown sentiment")
        return "neutral"
        

def get_sentiment(classifier, text):
    confidence_scores = classifier.tag_text(
        text=text,
        #"nlptown/bert-base-multilingual-uncased-sentiment"
        model_name_or_path="cardiffnlp/twitter-roberta-base-sentiment",
        mini_batch_size=1,
    )

    # This should only loop once
    for confidence_score in confidence_scores:
        s = calc_sentiment(confidence_score)
        if s is None:
            print("Error: sentiment is NoneType")
        if confidence_score.labels[0] is None:
            print("Error: Label 0 is NoneType")
        elif confidence_score.labels[1] is None:
            print("Error: Label 1 is NoneType")
        elif confidence_score.labels[2] is None:
            print("Error: Label 2 is NoneType")

        sentiment = Sentiment(
            s,
            confidence_score.labels[0].score,
            confidence_score.labels[1].score,
            confidence_score.labels[2].score)
        return sentiment


def assess(classifier, docs):
    print("Assessing 3-class sentiment")
    sentiments = []
    i = 0
    for doc in docs:
        #print("doc: ", doc)
        sentiment = get_sentiment(classifier, doc)
        
        if sentiment:
            sentiments.append(sentiment)
        else:
            print("Error: sentiment is NoneType")
        if i % 10 == 0:
            print("Processing doc: ", i)
        i = i + 1

    return sentiments
