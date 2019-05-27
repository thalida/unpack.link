# unpack.link

## Running locally
```
python server.py
rq worker controllers
rq worker unpackers
redis-server --daemonize yes
```

## Monitoring
```
rq-dashboard
```

