FROM python:3.8-slim
LABEL io.openshift.tags=prometheus,prometheus-exporter,mozilla-observatory \
    io.k8s.description="A prometheus exporter for metrics of Mozilla Observatory" \
    maintainer="Ando Roots <ando@sqroot.eu>"

EXPOSE 8080
WORKDIR /opt/observatory-exporter
ENV PYTHONPATH '/opt/observatory-exporter/'

COPY requirements.txt /opt/observatory-exporter/requirements.txt
RUN pip install -r /opt/observatory-exporter/requirements.txt && \
    rm -f /opt/observatory-exporter/requirements.txt
COPY src /opt/observatory-exporter/src

CMD ["python" , "/opt/observatory-exporter/src/collector.py"]
