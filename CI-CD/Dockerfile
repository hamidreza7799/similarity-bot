FROM gitlab/gitlab-runner:latest
LABEL MAINTAINER="Hamidreza Azarbad | hamidreza.azarbad77@gmail.com"

ARG ssh_pub_key

#RUN whoami
RUN usermod -aG root gitlab-runner
RUN touch /var/run/docker.sock
RUN chown gitlab-runner:root /var/run/docker.sock
RUN apt-get update && \
    apt-get install -y \
        git \
        openssh-server \
        docker.io \
        docker-compose
RUN usermod -aG docker gitlab-runner
RUN su - gitlab-runner
RUN gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.farakaft.ir/" \
  --registration-token "uJpzcgyWsMxY1Zq3qWob" \
  --executor "shell" \
  --description "Runner for similarity race bot in Desktop" \
  --tag-list "deploy,python,pyrogram" \
  --run-untagged="true" \
  --locked="false" \
  --access-level="not_protected"

RUN ssh-keygen -t rsa -N "" -f /home/gitlab-runner/.ssh
#RUN cat /home/gitlab-runner/.ssh/id_rsa.pub
