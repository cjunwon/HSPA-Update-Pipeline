FROM public.ecr.aws/docker/library/python:3.9.6

MAINTAINER "Adrian Lam"

# create working directory and install pip dependencies
WORKDIR /my_function
COPY requirements.txt requirements.txt

# RUN pip install fiona
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy python project files from local to /my_function image working directory
COPY . .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "python3","pci_update.py" ]