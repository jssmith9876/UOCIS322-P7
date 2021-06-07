FROM python:3.8
LABEL maintainer="jsmith37@uoregon.edu"
COPY . /website
WORKDIR /website
RUN pip install -r requirements.txt
CMD ["python", "website.py"]