
# mini elasticsearch

It has text search with TF-IDF

Phrase search to be implemented.

support for following schema only, will be improved.

```
{
"id": "1",
"title": "quick fox",
"data": "A fox is usually quick and brown."
}
```



Api endpoint for indexing
```
POST /index
{
"id": "1",
"title": "quick fox",
"data": "A fox is usually quick and brown."
}

200 OK

POST /index
{
"id": "2",
"title": "lazy dog"
"data": "A quick brown fox jumped over lazy dog. A fox is always jumping."
}

200 OK
```

Api endpoint for search
```
GET /search?q=quick%20fox

[
{
    "id": "1",
    "title": "quick fox",
    "data": "A fox is usually quick and brown."
},
{
    "id": "2",
    "title": "lazy dog"
    "data": "A quick brown fox jumped over lazy dog. A fox is always jumping."
}]


GET /search?q=dog

[
{
    "id": "2",
    "title": "lazy dog"
    "data": "A quick brown fox jumped over lazy dog. A fox is always jumping."
}]


GET /search?q=quick%20dog

[
{
    "id": "2",
    "title": "lazy dog"
    "data": "A quick brown fox jumped over lazy dog. A fox is always jumping."
},
{
    "id": "1",
    "title": "quick fox",
    "data": "A fox is usually quick and brown."
}]

```