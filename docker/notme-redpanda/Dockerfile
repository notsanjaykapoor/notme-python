FROM vectorized/redpanda:latest
USER root
RUN apt update && apt install -y python3-apt
USER redpanda
VOLUME [/host-data/redpanda]
