 # syntax=docker/dockerfile:1
FROM debian:stable

RUN apt-get update && apt install -y wget

RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb

RUN apt-get update && apt install -y python3 build-essential python3-pip curl git zip build-essential python3-wheel python3-demjson minify curl dotnet-sdk-7.0 jo jq

RUN python3 -m pip install --break-system-packages  GitPython Jinja2 markdown sphinx pylint 

VOLUME /var/www/release
ENV RUNNER_NAME="publisher"
ENV RUNNER_REPOSITORY_URL="https://github.com/intx82/esp32-mpy-uclient"
ENV GITHUB_ACCESS_TOKEN="AEGPBR5HDRDDDXKTIT3T6PLFIO6S4"
RUN mkdir -p /actions-runner && cd /actions-runner
RUN useradd -ms /bin/bash github
RUN chown github /actions-runner
ADD runner.sh /actions-runner/runner.sh
RUN chmod 0755 /actions-runner/runner.sh
USER github
WORKDIR /actions-runner

RUN curl -o /actions-runner/actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
RUN tar xzf /actions-runner/actions-runner-linux-x64-2.311.0.tar.gz
USER root
RUN /actions-runner/bin/installdependencies.sh
USER github
RUN /actions-runner/config.sh --url $RUNNER_REPOSITORY_URL --token $GITHUB_ACCESS_TOKEN
CMD ["/actions-runner/runner.sh"]
