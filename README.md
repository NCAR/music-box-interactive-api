# music-box-interactive
## User interface for the MusicBox box/column model

**Configure, run, and plot results for the MusicBox model, and edit chemical mechanisms.**

** Build and run

All configuration is handled by docker files and docker compose.

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
it reflected, run the below command and it should rebuild the server code. If you made a change to the web file, you'll have to edit Dockerfile.web and choose the branch your working on and manually rebuild the web files (`docker-compose build --no-cache web`).

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