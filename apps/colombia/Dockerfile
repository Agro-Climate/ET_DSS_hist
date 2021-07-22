FROM ubuntu:18.04
RUN apt-get update; apt-get install python3.8 python3-pip make ca-certificates cmake gfortran -y

COPY . /home/SIMAGRI/
WORKDIR /home/SIMAGRI/DSSAT/dssat-csm-os/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/home/SIMAGRI/DSSAT/dssat-base-files -DCMAKE_BUILD_TYPE=RELEASE ..; 
RUN make; make install

WORKDIR /home/SIMAGRI/
RUN mv TEST_CO/* DSSAT/dssat-base-files

WORKDIR /home/SIMAGRI/
RUN pip3 install -r requirements.txt
CMD ["python3", "index.py", "colombia"]