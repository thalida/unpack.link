# unpack.link

## Starting Services

Use `python contorller.py`

Web Server: `python contorller.py web-server`

Fetcher Queue: `python contorller.py fetcher`

Broadcaster Queue: `python contorller.py broadcaster`

## Documenation

Rebuild Docs: `make html -C docs/`

## Examples
### Twitter
```
thread_example = 1048986902098059267
quoted_example = 1048977169186271232
multi_quote_example = 1048991778119008258
simple_weird_tree = 1048989029486809088
medium_weird_tree = 1049037454710394881
large_weird_tree = 946823401217380358
deleted_quoted_tweet = 946795191784132610
```

# TODOs

## 8 June
- [x] Set general staleness checks (type has a default, rules can override)
- [ ] Start rendering nodes.
    - [ ] Setup vue.
    - [ ] Setup typescript
- [x] Move upnack folder to top level
- [x] Add better comments and documentation
    - [x] Figure out one of those self documenting sites (sphinx)


## Some Date
- flask app
- pass url to unpack.py api call
- setup json format for data
- return json


request url or id

if id exists
    check if the data is ready
    if ready
        show it
    else
        fire api call to get data
        show input to get notified/text to bookmark
else
    show error

if url
    id = get id for url
    redirect to id

pk_id <==> path
pk_id, date, path, meta
pk_id, pk_id, relationship (quote, reply, link)


