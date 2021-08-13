# SIMAGRI Agricultural Simulator

Built using Docker, Podman, Python 3.8, Dash Plotly, and DSSAT (https://dssat.net/), How to compile DSSAT on Linux (https://dssat.net/210/).

Three versions of SIMAGRI have been developed for the following countries:

- Ethiopia
- Senegal
- Colombia

For each country SIMAGRI enables crop simulation either based on historical weather data or as a forecast.

SIMAGRI Ethiopia: http://simagri-ethiopia1.iri.columbia.edu/historical

## Instructions to run SIMAGRI locally:

1. Install Docker. The installer can be found here: [[WIN]](https://docs.docker.com/docker-for-windows/install/) [[OSX]](https://docs.docker.com/docker-for-mac/install/) [[LINUX]](https://docs.docker.com/engine/install/). 

2. Install Podman. The installer can be found [HERE](https://podman.io/getting-started/installation). 

3. Clone this repo: 

> `git clone git@github.com:Agro-Climate/ET_DSS_hist.git`
>
> `cd ET_DSS_hist`
>
> `git checkout ET_DSS_hist_Linux`

<br> 

## Steps `4-6` should be used if using Docker and steps `7-9` should be used if using Podman.
## Due to the similarities of the different localizations of SIMAGRI the app is structured so files unique to each country are stored in apps/\<country>
## The following commands will allow building Docker images for each country and running them as Docker containers
<br> 

## Docker Instructions

4. Build a Docker image for desired country:

> `docker build -f ./apps/<country>/Dockerfile -t simagri_<country>_img:latest .`

5. Run a Docker container for desired country:

> `docker run --name=simagri_<country> -e PYTHONUNBUFFERED=1 --rm -dp <port>:5000 simagri_<country>_img:latest`

After running this command the app may be viewed at localhost:\<port> (when deploying to production on a server port 80 should be used)

The following command may also be used to allow tracking of the command line output of the docker container:
> `docker logs --follow simagri_<country>`

6. Kill a running container and clear unused resources `(optional)`:

> `docker kill simagri_<country>`

> `docker image prune -af`

## Podman Instructions `(requires root privileges)`

7. Build an image for desired country using Podman:

> `podman build -f ./apps/<country>/Dockerfile --pull-never -t simagri_<country>_img .`

8. Run a container for desired country using Podman:

> `sudo podman run --name=simagri_<country> -e PYTHONUNBUFFERED=1 --rm -dp <port>:5000 simagri_<country>_img`

After running this command the app may be viewed at localhost:\<port> (when deploying to production on a server port 80 should be used)

The following command may also be used to allow tracking of the command line output of the container:
> `sudo podman logs --follow simagri_<country>`

9. Kill a running container and clear unused resources `(optional)`:

> `sudo podman kill simagri_<country>`

> `podman image prune -f`
