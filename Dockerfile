FROM python:latest
COPY server.py /
RUN pip3 install ply psutil
EXPOSE 8080
CMD ["python3", "server.py"]

