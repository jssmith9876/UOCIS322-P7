FROM python:3.8
LABEL maintainer="jsmith37@uoregon.edu"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "flask_brevets.py"]