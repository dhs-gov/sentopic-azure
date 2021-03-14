# SenTopic for Azure

Version: 0.1a

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) 


SenTopic combines sentiment analysis and topic modeling into a single capability allowing for sentiment to be derived per generated topic and for topics to be derived per generated sentiment. This version of SenTopic is implemented as an asynchronous Azure Durable Function service and includes required Azure modules for endpoint, orchestrator, and activity.

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
| "Having to report to work without being provided PPE." | 3 | 0 | negative | 1_star |
| "Teleworking at home." | 3 | 2 | neutral | 3_stars |
| "Things are good. Im ready to do the mission." | 3 | 1 | positive | 4_stars |


# API (v1)

## Submit Data

Description: Submit data for analysis.  
Method:  `POST`  
URL:  `https://<domain>/sentopic`   

## Request

| Key | Value | Required | Description |
| :--- | :----: | :----: | :----: |
| None | None | NA | No query parameters required for v1.|

## Headers

| Key | Value | Required | Description |
| :--- | :--- | :----: | :--- |
| `Content-Type` | `application/json`<br>`multipart/form-data` | Yes | Specify <i>either</i> JSON or multi-part form payloads. If both JSON and multi-part form payloads are submitted, the JSON payload must be attached as a file (See Multipart Form Data). |

## Body / Payload
### JSON
SenTopic payloads require a `documents` key that defines a list of JSON objects, each of which consists of a `text` key and a document (or paragraph) string value. Optionally, a list of stop words may be added for the corpus domain using the `stopwords` key.

```bash
curl --location --request POST 'https://<domain>/sentopic'
    --header 'Content-Type: application/json'
    --data-raw '{
        "documents": 
            [
                {
                    "text": "Having to report to work without being provided PPE."
                }
                ,
                {
                    "text": "Teleworking at home."
                }
                ,
                {
                    "text": "Things are good. Im ready to do the mission."
                }

                ...
            ],
        "stopwords":
            [
                "the", "list", "of", "stop", "words", "go", "here"
            ]
    }   '

```

### Multipart Form Data 
SenTopic supports one or more file attachments. The supported file types include:

| Type | Available | Description |
| :--- | :---: | :--- |
| `.txt` | Yes | Text file with one document per line. For stop words list, one stop word per line.|
| `.json` | Yes | Requires `documents` key containing list of `text` value pairs.|
| `.csv` | Yes | Requires one column of data, no headers, with one document per row.|
| `.xlsx` | No | Coming soon.|
| `.docx` | No | Coming soon.|
| `.pptx` | No | Coming soon.|


Note that each file attachment may use the same `file` parameter name. Optionally, a stop words list may be added using the file name `stopwords.txt`. 

```bash
curl --location --request POST 'https://<domain>/sentopic' 
    --header 'Content-Type: multipart/form-data' 
    --form 'file=@"data_file.json"' 
    --form 'file=@"data_file.csv"' 
    --form 'file=@"stopwords.txt"' 
```

## Response
Due to the asynchronous nature of Azure Durable Functions, a request to SenTopic will return a  set of Azure service endpoints that may be used to invoke further actions, such as retrieving results. These endpoints are defined in the [Azure HttpManagementPayload API](https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.webjobs.extensions.durabletask?view=azure-dotnet) and include:

| Service | Description |
| :--- | :--- | 
| statusQueryGetUri | Gets the HTTP GET status query endpoint URL. If completed, return result.|
| sendEventPostUri | Gets the HTTP POST external event sending endpoint URL.|
| terminatePostUri | Gets the HTTP POST instance termination endpoint.|
| purgeHistoryDeleteUri | Gets the HTTP DELETE purge instance history by instance ID endpoint.|

Azure returns this set of endpoints as a JSON object.

```json
{
    "id": "1befa48c1d4644c7856803c0b3c797b9",
    "statusQueryGetUri": "http://localhost:7071/runtime/webhooks/durabletask/a",
    "sendEventPostUri": "http://localhost:7071/runtime/webhooks/durabletask/b",
    "terminatePostUri": "http://localhost:7071/runtime/webhooks/durabletask/c",
    "rewindPostUri": "http://localhost:7071/runtime/webhooks/durabletask/d",
    "purgeHistoryDeleteUri": "http://localhost:7071/runtime/webhooks/durabletask/e"
}
```

## Response Codes
Due to the asynchronous nature of Azure Durable Functions, a request to SenTopic will normally result in an `HTTP 202 Accepted` after SenTopic has received all data. 

| Code | Payload | Description |
| :--- | :----: | :--- |
| `202` | Azure Endpoints | Submission successfully accepted. Multiple Azure endpoint URLs are returned to further actions, such as retrieving results.|
| `400` | Error Message | Invalid input.|
| `500` | None | System internal error.|

## Results
SenTopic results are available from the `statusQueryGetUri` endpoint after SenTopic has completed processing the data. <i>NOTE: Azure Durable Functions return JSON results as a double-quoted string and adds escaped double quotes around keys and values.</i>. 

The following shows partial results without surrounding double quotes or quoted keys and values.

```json
{
    "name": "sentopic",
    "instanceId": "34521eb8bca84a568e60c33a92a10e6f",
    "runtimeStatus": "Completed",
    "input": 
        [
            "Having to report to work without being provided PPE."
            , 
            "Teleworking at home."
            , 
            "Things are good. Im ready to do the mission."
            ,
            ...
        ]
        ,
    "output": [
        {
            "result": 
                [
                    {
                        "text": "Having to report to work without being provided PPE.", 
                        "bertopic": 3, 
                        "lda": 0, 
                        "class3": "negative", 
                        "star5": "1_star"
                    }
                    , 
                    {
                        "text": "Teleworking at home.", 
                        "bertopic": 3, 
                        "lda": 2, 
                        "class3": "neutral",
                        "star5": "3_stars"
                    }
                    , 
                    {
                        "text": "Things are good. Im ready to do the mission.", 
                        "bertopic": 3, 
                        "lda": 1, 
                        "class3": "positive",
                        "star5": "4_stars"
                    }
                    ,
                    ...
                ]
                ,
            "bert_topics": 
                [
                    [
                        {
                            "word": "office", 
                            "weight": "0.02923134401914028"
                        }
                        ,
                        {
                            "word": "worried", 
                            "weight": "0.024890853269684016"
                        }
                        , 
                        {
                            "word": "pandemic", 
                            "weight": "0.017575496779442725"
                        }
                        ,
                        ...
                    ]
                ]
                , 
               [
                    [
                        {
                            "word": "office", 
                            "weight": "0.02923134401914028"
                        }
                        ,
                        {
                            "word": "worried", 
                            "weight": "0.024890853269684016"
                        }
                        , 
                        {
                            "word": "pandemic", 
                            "weight": "0.017575496779442725"
                        }
                        ,
                        ...
                    ]
                ]
                , 
                ...


            "lda_topics": 
                [
                    [
                        {
                            "word": "worried", 
                            "weight": "0.03428619358724741"
                        }
                        ,
                        {
                            "word": "unnecessary", 
                            "weight": "0.017143082435909174"
                        }
                        , 
                        {
                            "word": "medical", 
                            "weight": "0.017143082435909174"
                        }
                        ,
                        ...
                    ]
                ]
                , 
        }
    ],
    "createdTime": "2021-03-14T06:34:10Z",
    "lastUpdatedTime": "2021-03-14T06:34:43Z"
}

Here, note that `output` contains `result`, `bert_topics`, and `lda_topics` keys. The `result` key contains a list of JSON objects for each document that includes the document text, its sentiment values, and its derive topic numbers. The `bert_topics` key contains the list of significant keywords or phrases 
