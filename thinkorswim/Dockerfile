FROM centos:7

RUN yum update -y \
  && yum -y install unzip \
  && yum -y install java-1.8.0-openjdk-devel \
  && yum clean all
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0
ENV PATH "$PATH":/${JAVA_HOME}/bin:.:

RUN yum install -y wget

RUN wget https://mediaserver.thinkorswim.com/installer/InstFiles/thinkorswim_installer.sh

RUN printf "1\no\n1\n2\n1\n\nn\nn\n" | bash thinkorswim_installer.sh

ENV HOME /root
#CMD /usr/local/thinkorswim/thinkorswim

# Replace 0 with your user / group id
RUN export uid=1000 gid=1000
RUN mkdir -p /home/developer
RUN echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd
RUN echo "developer:x:${uid}:" >> /etc/group
RUN echo "developer ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN chmod 0440 /etc/sudoers
RUN chown ${uid}:${gid} -R /home/developer

USER developer
ENV HOME /home/developer

RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/America/Chicago /etc/localtime

CMD bash /usr/local/thinkorswim/thinkorswim && /bin/bash


