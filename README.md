# MusicBox Interactive API Server

[![Tests](https://github.com/NCAR/music-box-interactive-api/actions/workflows/pytest.yml/badge.svg)](https://github.com/NCAR/music-box-interactive-api/actions/workflows/pyteset.yml)

## User interface for the MusicBox box/column model

**Configure, run, and plot results for the MusicBox model, and edit chemical mechanisms.**

## Build and run

All configuration is handled by docker files and docker compose. First navigate to the project directory.

To build
```
docker compose build
```

To run
```
docker compose up
```

You can press CTRL-C to quite docker compose.

Docker-compose will cache file builds and volumes. If you make a change and you want to see 
it reflected, run the below command and it should rebuild the server code.

```
docker compose down -v \
    && docker compose build \
    && docker compose up --force-recreate
```

If you need to remove absolutely everything

```
docker compose down -v --rmi all \
    && docker system prune \
    && docker compose build --no-cache \
    && docker compose up --force-recreate
```

If you would like to run docker in a deteched state, add the `-d` flag like this

```
docker compose up -d
```

If you would like to view the logs after starting docker in a detach state, you can do so like this

```
docker compose logs -f
```

## Web Files

This repository is only the API server for MusicBox Interactive. If you wish to run the web files, head over to [music-box-interactive-client](https://github.com/NCAR/music-box-interactive-client)

## RabbitMQ Admin

After running `docker compose up -d` you can navigate to the RabbitMQ [http://localhost:15672](http://localhost:15672) admin interface to monitor the queues.
The username is `guest` and the password is `guest`.