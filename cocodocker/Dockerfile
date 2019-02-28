FROM ubuntu:16.04
MAINTAINER Waleed Abdulla <waleed.abdulla@gmail.com>
# https://github.com/waleedka/modern-deep-learning-docker/blob/master/Dockerfile

# Supress warnings about missing front-end. As recommended at:
# http://stackoverflow.com/questions/22466255/is-it-possibe-to-answer-dialog-questions-when-installing-under-docker
ARG DEBIAN_FRONTEND=noninteractive


# Essentials: developer tools, build tools, OpenBLAS
RUN apt-get update && apt-get install -y --no-install-recommends \
apt-utils git curl vim unzip openssh-client wget \
build-essential cmake \
libopenblas-dev


#
# Python 3.5
#
# For convenience, alias (but don't sym-link) python & pip to python3 & pip3 as recommended in:
# http://askubuntu.com/questions/351318/changing-symlink-python-to-python3-causes-problems
RUN apt-get install -y --no-install-recommends python3.5 python3.5-dev python3-pip python3-tk && \
pip3 install --no-cache-dir --upgrade -I pip==18.1 setuptools==40.6.3 && \
echo "alias python='python3'" >> /root/.bash_aliases && \
echo "alias pip='pip3'" >> /root/.bash_aliases
# Pillow and it's dependencies
RUN apt-get install -y --no-install-recommends libjpeg-dev=8c-2ubuntu8 zlib1g-dev=1:1.2.8.dfsg-2ubuntu4.1 && \
pip3 --no-cache-dir install -I Pillow==5.4.1
# Science libraries and other common packages
RUN pip3 --no-cache-dir install -I \
numpy==1.16.0 scipy==1.2.0 sklearn==0.0 scikit-image==0.14.2 pandas==0.23.4 matplotlib==3.0.2 Cython==0.29.3 requests==2.21.0


#
# PyCocoTools
#
# Using a fork of the original that has a fix for Python 3.
# I submitted a PR to the original repo (https://github.com/cocodataset/cocoapi/pull/50)
# but it doesn't seem to be active anymore.
#RUN pip3 install --no-cache-dir git+https://github.com/waleedka/coco.git#subdirectory=PythonAPI
RUN pip3 install --no-cache-dir git+https://github.com/cocodataset/cocoapi.git@ed842bffd41f6ff38707c4f0968d2cfd91088688#subdirectory=PythonAPI


##
## Graph-tool
##
#RUN echo deb http://downloads.skewed.de/apt/xenial xenial universe >> /etc/apt/sources.list && \
#	echo deb-src http://downloads.skewed.de/apt/xenial xenial universe >> /etc/apt/sources.list
#RUN apt-get update && \
#	apt-get install -y --allow-unauthenticated libcairo2-dev=1.14.6-1 python3-graph-tool=2.27-1
#RUN pip3 install --no-cache-dir -I pycairo==1.18.0

#
#NetworkX
#
RUN pip3 install --no-cache-dir -I networkx==2.2


#
# Get annotations coco file
#
RUN mkdir -p /srv/datas
WORKDIR /srv/datas
RUN wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip && \
	unzip annotations_trainval2017.zip && \
	rm annotations_trainval2017.zip
RUN wget http://images.cocodataset.org/annotations/annotations_trainval2014.zip && \
	unzip annotations_trainval2014.zip && \
	rm annotations_trainval2014.zip

RUN mkdir -p /srv/app
WORKDIR /srv/app

#
# Copy and run sample script
#
#COPY cocoget.py .
#RUN python3 cocoget.py


#WORKDIR "/root"
#CMD ["/bin/bash"]