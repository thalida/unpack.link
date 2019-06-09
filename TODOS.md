# TODO

## 8 June
- [] Set general staleness checks (type has a default, rules can override)
- [] Start rendering nodes.
    - [] Setup vue.
    - [] Setup typescript
- [x] Move upnack folder to top level
- [] Add better comments and documentation
    - [] Figure out one of those self documenting sites (sphinx)


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

