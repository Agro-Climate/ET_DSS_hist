# ET DSS Tool 

A minimal working version of ET DSS using Docker, Flask and Heroku.

A demo is hosted [here](https://ethiopia-dss-demo.herokuapp.com/).

## Warning for Deployment on Linux:
- `Summary.OUT` (not SUMMARY)
-  There shouldn't be any executable named `DSCSM047.EXE`.

## Prerequisites:

- Docker
- Heroku
- VS Code + Docker Extension

## Steps (Local test) 

Following are the steps for testing this app on Windows.


Steps `4` and `5` are not necessary if the Heroku app is connected to the Github repo (from the heroku dashboard) 

1. The first step requires the installation of Docker. The installer can be found [here](https://docs.docker.com/docker-for-windows/install/). 

2. Clone this repo: 

> `git clone https://github.com/Agro-Climate/ET_DSS_hist`
> 
> `cd ET_DSS_hist`

3. From within the local repo, build the Dockerfile:

> `docker.exe build --tag <container_name_here> .`

4. Then run the app locally:

> `docker.exe run -p 5000:5000 <container_name_here> `


5. (First Time) For registering and deploying the app on Heroku:

> `heroku login`
>
> `heroku container:login`
>
> `heroku create <app_name_here>`
>
> `heroku container:push web --app <app_name_here>`
>
> `heroku container:release web --app <app_name_here>`

6. For existing app

> `heroku login`
>
> `heroku container:login`
>
> `heroku git:remote -a <app_name_here>`
>
> `git add .`
>
> `git commit -am "description"`
>
> `heroku container:push web --app <app_name_here>`
>
> `heroku container:release web --app <app_name_here>`