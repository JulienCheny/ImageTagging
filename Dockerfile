FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

# Supress warnings about missing front-end
ARG DEBIAN_FRONTEND=noninteractive

# install
RUN \
	apt-get update && apt-get install -y \
	autoconf \
    automake \
	libtool \
	build-essential \
	git

# addons
RUN \
	apt-get install -y --no-install-recommends \
	wget \
    curl \
    vim \
    unzip \
    openssh-client \
    cmake \
    libopenblas-dev \
    software-properties-common
    


################################################# Python part ####################################################



#
# Python 3.5
#
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y --no-install-recommends python3.6 python3.6-dev python3-pip python3-tk && \
pip3 install --no-cache-dir --upgrade -I pip==19.0.3 setuptools==40.8.0 && \
echo "alias python='python3'" >> /root/.bash_aliases && \
echo "alias pip='pip3'" >> /root/.bash_aliases
# Pillow and it's dependencies
RUN apt-get install -y --no-install-recommends libjpeg-dev=8c-2ubuntu8 zlib1g-dev=1:1.2.11.dfsg-0ubuntu2 && \
pip3 --no-cache-dir install -I Pillow==5.4.1
# Science libraries and other common packages
RUN pip3 --no-cache-dir install -I \
numpy==1.16.0 scipy==1.2.0 sklearn==0.0 scikit-image==0.14.2 pandas==0.23.4 matplotlib==3.0.2 Cython==0.29.3 requests==2.21.0

#
# PyCocoTools
#
RUN pip3.6 install --no-cache-dir -I pycocotools==2.0.0

#
#NetworkX
#
RUN pip3 install --no-cache-dir -I networkx==2.2

#
# Get annotations coco file
#
#RUN mkdir -p /srv/datas
WORKDIR /srv/datas
RUN wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip && \
	unzip annotations_trainval2017.zip && \
	rm annotations_trainval2017.zip
RUN wget http://images.cocodataset.org/annotations/annotations_trainval2014.zip && \
	unzip annotations_trainval2014.zip && \
	rm annotations_trainval2014.zip



################################################## Yolo part #####################################################



# build repo
WORKDIR /srv
RUN \
	git clone https://github.com/pjreddie/darknet # Tested with the commit 61c9d02 on 14 Sep 2018

# make
WORKDIR /srv/darknet/
RUN sed -i 's/GPU=.*/GPU=1/' Makefile && \
	make

# download yolov3 tiny weights
RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights >/dev/null 2>&1

WORKDIR /srv

# test nvidia docker
CMD nvidia-smi -q

# defaults command
CMD ["bash"]
