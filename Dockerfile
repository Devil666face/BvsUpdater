FROM python:3.11
WORKDIR /BvsUpdater
VOLUME /BvsUpdater/bases
RUN apt-get update && \
    apt-get install wine -y && \
    apt-get install p7zip -y && \
    apt-get install p7zip-full -y && \
    apt-get install curl -y && \
    apt-get install sshfs -y && \
    apt-get install tar -y && \
    apt-get install rsync -y && \
    apt-get install zip -y
COPY requirements.txt .
COPY . .
COPY .env .
RUN tar -xzf ksc/util.tar.gz_ -C ksc/
RUN pip install -r requirements.txt
RUN cp agent.key drw/DRW_ESS10/ && \
    cp agent.key drw/DRW_ESS11/ && \
    cp agent.key drw/DRW_ESS11.00.0,2/ && \
    cp agent.key drw/DRW_ESS13/ && \
    cp agent.key drw/DRW_SS10/ && \
    cp agent.key drw/DRW_SS11.5/ && \
    cp agent.key drw/DRW_SS11/ && \
    cp agent.key drw/DRW_SS9/
#ENV KPDA_USER=$KPDA_USER \
#    KPDA_PASSWORD=$KPDA_PASSWORD \
#    ESS6_USERNAME=$ESS6_USERNAME \
#    ESS6_PASSWORD=$ESS6_PASSWORD \
#    ESS6_IP=$ESS6_IP 
CMD ["python", "main.py"]
