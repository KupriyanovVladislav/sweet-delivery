# Dockerfile
FROM python:3.8
WORKDIR /sweet_delivery
COPY . /sweet_delivery
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
#ENTRYPOINT ["./docker-entrypoint.sh"]