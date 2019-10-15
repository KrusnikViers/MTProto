FROM python:3-slim

# Install dependencies.
# Clone MTProto server and build it from sources.
# Remove temporary files, source files, and dependencies that was needed only for building.
RUN pip3 install --no-cache-dir --upgrade requests==2.19              && \
    apt-get update                                                    && \
    apt-get install -y git build-essential libssl-dev zlib1g-dev curl && \
    mkdir /build                                                      && \
    cd /build                                                         && \
    git clone https://github.com/TelegramMessenger/MTProxy .          && \
    make                                                              && \
    mkdir /server                                                     && \
    cp /build/objs/bin/* /server                                      && \
    cd /server                                                        && \
    rm -rf /build                                                     && \
    apt-get purge -y git build-essential libssl-dev zlib1g-dev        && \
    apt-get autoremove -y                                             && \
    apt-get clean                                                     && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY src /src
CMD ["/src/entry.sh"]
