# SenTopic

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
| This is a double-edged sword. The limits for this technically nuanced aspect of the program were problematic maybe unrealistic. | -1	| 3	| negative | 2_stars |
| It wasnt overly burdensome on Phase I as long as it gave the government what they needed to make a response. | 2	| 1	| neutral |	3_stars |
| It introduced efficiencies on the offerors side and the governments side. Time and resources were saved by both during the initial phase. | 2	| 1	| positive | 5_stars |


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
| `Content-Type` | `application/json`<br>`multipart/form-data` | Yes | Specify <i>either</i> JSON or multi-part form payload. If both JSON and multi-part form payloads are submitted, the JSON payload must be attached as a file (See Multipart Form Data). |

## Body / Payload
### JSON
JSON payloads require a `documents` key that defines a list of JSON objects, each of which consists of a `text` key and a document (or paragraph) string value.

```bash
curl --location --request POST 'https://<domain>/sentopic'
    --header 'Content-Type: application/json'
    --data-raw '{
        "documents": [
            {
                "text": "This is a test of the SenTopic Azure Durable Function. It is great."
            },
            {
                "text": "This is another test of the SenTopic Azure Durable Function."
            }
        ]
    }'
```

### Multipart Form Data 
SenTopic supports one or more file attachments. The supported file types include:

| Type | Available | Description |
| :--- | :---: | :--- |
| .txt | Yes | Text file with one document per line.|
| .json | Yes | Requires `documents` key containing list of `text` value pairs.|
| .csv | Yes | Requires one column of data, no headers, with one document per row.|
| .xlsx | No | Coming soon.|
| .docx | No | Coming soon.|
| .pptx | No | Coming soon.|


Note that each file attachment may use the same `file` keyword.

```bash
curl --location --request POST 'https://<domain>/sentopic' 
    --header 'Content-Type: multipart/form-data' 
    --form 'file=@"data_file.json"' 
    --form 'file=@"data_file.csv"' 
```

## Response
Due to the asynchronous nature of Azure Durable Functions, a request to SenTopic will return a JSON list of service endpoints that may be accessed to invoke further actions on the service. These endpoints are defined in the [Azure HttpManagementPayload API](https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.webjobs.extensions.durabletask?view=azure-dotnet) and include:

| Service | Description |
| :--- | :--- | 
| statusQueryGetUri | Gets the HTTP GET status query endpoint URL. If completed, return result.|
| sendEventPostUri | Gets the HTTP POST external event sending endpoint URL.|
| terminatePostUri | Gets the HTTP POST instance termination endpoint.|
| purgeHistoryDeleteUri | Gets the HTTP DELETE purge instance history by instance ID endpoint.|

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
Due to the asynchronous nature of Azure Durable Functions, a request to SenTopic will normally result in an `HTTP 202 Accepted` after it has received all data. 

| HTTP Code | Payload | Description |
| :--- | :----: | :--- |
| `202` | Multiple Links | Submission successfully accepted. Multiple URL links are returned to allow for checking the status of processing as well as retrieving results.|
| `400` | Error Message | Invalid input.|
| `500` | None | System internal error.|

## Results
SenTopic results are available from the return `statusQueryGetUri` endpoint after SenTopic has completed processing the data. <i>NOTE: Azure Durable Functions return JSON results as a double-quoted string. In addition, Azure Durable Functions adds escaped double quotes around keys and values in the JSON output</i>. The following shows the JSON output without surrounding double quotes and escaped double quotes.

```json
{
    "name":"sentopic",
    "instanceId":"6ac3135add3e4ab88add88e0ba6c05bc",
    "runtimeStatus":"Completed",
    "input":"[\"This is the first document. \", \"This is another document. It is a fine document. \"]",
    "customStatus":"NOTE: Asynchronous Azure Durable Functions add quotes around JSON output and also escape double quotes for JSON keys.",
    "output":["
        {\"paras\": 
            [{\"text\": \"This is the first document.\", 
            \"bertopic\": -1, 
            \"lda\": 3, 
            \"class3\": \"negative\", 
            \"star5\": \"4_stars\"}, 
        
            {\"text\": \"This is another document. It is a fine document.\",       
            \"bertopic\": 0, 
            \"lda\": 2, 
            \"class3\": \"positive\", 
            \"star5\": \"5_stars\"}, 

            ...

            "],"createdTime":"2021-03-13T13:27:32Z","lastUpdatedTime":"2021-03-13T13:28:07Z"}
    ],
    "createdTime": "2021-03-13T12:59:48Z",
    "lastUpdatedTime": "2021-03-13T13:00:21Z"
}
```

Note that `bert_topics` and `lda_topics` may be empty if insufficient data was provided to derive topics.

## BERTopic Example


## LDA Example


