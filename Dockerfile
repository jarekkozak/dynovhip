FROM python:3.9-slim

WORKDIR /app

COPY dns.py .

#RUN pip install pygame --pre
RUN pip install --no-cache-dir requests ovh 

# -u unbuffered 
CMD ["python","-u", "./dns.py"]
