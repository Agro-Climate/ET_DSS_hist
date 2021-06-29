# ET DSS Tool 

A minimal working version of ET DSS using Docker, Flask and Heroku.

The first demo is hosted [here](https://ethiopia-dss-demo.herokuapp.com/).
Actual working version for Ethiopia is hosted [here] (https://simagri-et.herokuapp.com/).

## Warning for Deployment on Linux:
- `Summary.OUT` (not SUMMARY)
-  There shouldn't be any executable named `DSCSM047.EXE`.

## Prerequisites:

- Docker
- Terraform
- Heroku
- VS Code + Docker Extension

## Steps (Local test) 

# Terraform Setup (Linux)
# https://computingforgeeks.com/how-to-install-terraform-on-ubuntu-centos-7/

# assumes docker is installed

# get terraform latest version:

curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest | grep tag_name | cut -d: -f2 | tr -d \"\,\v | awk '{$1=$1};1'

# install the latest terraform (currently 1.0.1)

wget https://releases.hashicorp.com/terraform/[version]/terraform_[version]_linux_amd64.zip

mv terraform_[version]_linux_amd64.zip ~
cd

unzip terraform_[version]_linux_amd64.zip

# install the terraform executable
sudo mv terraform /usr/local/bin/

# 'terraform -v' should now work

# main.tf contains the terraform configuration

# build terraform infrastructure 
terraform init
terraform plan
terraform apply
# now you have the docker container for simagri deployed locally with terraform


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