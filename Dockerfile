FROM python:3.7
RUN pip install requests pandas pytest
RUN mkdir /data
COPY nemweb/ /nemweb/
ENV PYTHONPATH="$PYTHONPATH:/nemweb"
CMD ["python", "/nemweb/test.py"]
