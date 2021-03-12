# SenTopic

Version: 0.1a

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) 


SenTopic combines sentiment analysis and topic modeling into a single capability allowing for sentiment to be derived per generated topic and for topics to be derived per generated sentiment. 

## Sentiment Analysis

Sentiment analysis is performed using [AdaptNLP](https://github.com/Novetta/adaptnlp) with state-of-the-art (SOTA) [Hugging Face Transformers](https://github.com/huggingface/transformers).  SenTopic uses two separate transformers to provide two types of sentiment analysis:

1. [RoBERTa Base Sentiment](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment) for 3-class sentiment (negative, neutral, positive) -- based on Facebook AI's [RoBERTa](https://ai.facebook.com/blog/roberta-an-optimized-method-for-pretraining-self-supervised-nlp-systems/)
2. [BERT Base Multilingual Uncased Sentiment](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment) for 5-star sentiment (1 star, 2 stars, ..., 5 stars)] -- based on Google's [Bidirectional Encoder Representations from Transformers (BERT)](https://en.wikipedia.org/wiki/BERT_(language_model))


## Topic Modeling

SenTopic provides two types of topic modeling: [Latent Dirichlet Allocation (LDA)](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) and transformer-based [BERTopic](https://github.com/MaartenGr/BERTopic). While LDA provides de facto, statistical-based topic modeling, BERTopic provides SOTA-level performance using [Hugging Face Transformers](https://github.com/huggingface/transformers). Transformers that have been tested include:

1. [BERT Base Uncased](https://huggingface.co/bert-base-uncased) -- based on Google's [Bidirectional Encoder Representations from Transformers (BERT)](https://en.wikipedia.org/wiki/BERT_(language_model))
2. [XLM RoBERTa Base](https://huggingface.co/xlm-roberta-base) -- based on [XLM-RoBERTa](https://huggingface.co/transformers/model_doc/xlmroberta.html)


## Combining Sentiment Analysis and Topic Modeling

SenTopic combines sentiment analysis and topic modeling by performing both at the document (i.e., paragraph) level for a corpus, the results of which can then be represented by a table as shown below.

| Document | BERT Topic | LDA Topic | 3-Class Sentiment | 5-Class Sentiment |
| :--- | :----: | :----: | :----: | :----: |
| This is a double-edged sword. The limits for this technically nuanced aspect of the program were problematic maybe unrealistic. | -1	| 3	| negative | 2_stars |
| It wasnt overly burdensome on Phase I as long as it gave the government what they needed to make a response. | 2	| 1	| neutral |	3_stars |
| It introduced efficiencies on the offerors side and the governments side. Time and resources were saved by both during the initial phase. | 2	| 1	| positive | 5_stars |


