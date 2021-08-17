# FROM ubuntu:18.04
# RUN apt-get update; apt-get install python3.8 python3-pip make ca-certificates cmake gfortran -y

# COPY ./DSSAT /home/SIMAGRI/DSSAT
# WORKDIR /home/SIMAGRI/DSSAT/dssat-csm-os/build
# RUN cmake -DCMAKE_INSTALL_PREFIX=/home/SIMAGRI/DSSAT/dssat-base-files -DCMAKE_BUILD_TYPE=RELEASE ..; 
# RUN make; make install

# COPY ./requirements.txt /home/SIMAGRI
# WORKDIR /home/SIMAGRI/
# RUN pip3 install -r requirements.txt

FROM irikesha/simagridssat:latest

RUN pip3 install exp-mixture-model

COPY ./*.py /home/SIMAGRI/
COPY ./apps/ /home/SIMAGRI/apps/
COPY ./assets/ /home/SIMAGRI/assets/
COPY ./data/ /home/SIMAGRI/data/
COPY ./TEST_SN/* DSSAT/dssat-base-files/

WORKDIR /home/SIMAGRI/
CMD ["python3", "index.py", "senegal"]