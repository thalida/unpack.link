# unpack.link

## Starting Services
Run `docker-compose up --build`
Run `npm run serve`
Check that it's running with `docker ps`


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
- [x] Set general staleness checks (type has a default, rules can override)
- [x] Setup vue.
- [x] Setup typescript
- [ ] Index view
    - [x] Form enter a url, get redirected to results view
    - [ ] Use custom validation messages/display
- [ ] Results view
    - [x] has url field (silent refreshing(?))
    - [ ] query controls
    - [x] hit api endpoints
    - [x] socketio setup
    - [x] render node on socket push
    - [x] setup proper storage
    - [ ] Levels
        - [x] Render each link in it's level
        - [ ] not from same domain, then same domain
        - [ ] order both by order found on page
    - [ ] Add checkbox to show the links available with that link
    - [ ] fetch site data for node on quick view load
- [x] Update python functions to use proper/better named param style
- [x] Move upnack folder to top level
- [ ] Fetching
    - [ ] Cache db queries
    - [ ] Don't fetch css or fonts
    - [ ] Don't store site contents
    - [ ] Store link index on page
- [-] Add better comments and documentation
    - [x] Figure out one of those self documenting sites (sphinx)
    - [-] Vue/JS autodocs(?)
- [x] split out important shit from __init__ it's okay for readability!!!
- [x] change any print statements to log.info things
- [x] move broadcaster to be under queue manager
- [x] figure out why queues aren't being deleted
