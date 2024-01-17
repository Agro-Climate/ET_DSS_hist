# SIMAGRI Agricultural Simulator

Built using Docker, Python 3.8, Dash Plotly, and DSSAT (https://dssat.net/), How to compile DSSAT on Linux (https://dssat.net/210/).

Three versions of SIMAGRI have been developed for the following countries:

- Ethiopia
- Senegal
- Colombia

For each country SIMAGRI enables crop simulation either based on historical weather data or as a forecast.

SIMAGRI Ethiopia: http://simagri-ethiopia.iri.columbia.edu/historical

## Instructions to run SIMAGRI locally:

1. Install Docker. The installer can be found here: [[WIN]](https://docs.docker.com/docker-for-windows/install/) [[OSX]](https://docs.docker.com/docker-for-mac/install/) [[LINUX]](https://docs.docker.com/engine/install/). 

2. Clone this repo: 

> `git clone git@github.com:Agro-Climate/ET_DSS_hist.git`
>
> `cd ET_DSS_hist`
>
> `git checkout ET_DSS_hist_Linux`

<br> 

## Due to the similarities of the different localizations of SIMAGRI the app is structured so files unique to each country are stored in apps/\<country>
## Steps `3-5` will allow building Docker images for each country and running them as Docker containers
<br> 

3. Build a Docker image for desired country:

> `docker build -f ./apps/<country>/Dockerfile -t simagri_<country>_img:latest --network=host .`

4. Run a Docker container for desired country:

> `docker run --name=simagri_<country> -e PYTHONUNBUFFERED=1 --rm -dp <port>:5000 simagri_<country>_img:latest`

After running this command the app may be viewed at localhost:\<port> (when deploying to production on a server port 80 should be used)

The following command may also be used to allow tracking of the command line output of the docker container:
> `docker logs --follow simagri_<country>`

5. Kill a running container and clear unused resources `(optional)`:

> `docker kill simagri_<country>`

> `docker image prune -af`
