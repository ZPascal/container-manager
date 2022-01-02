FROM container-manager:latest
MAINTAINER Pascal Zimmermann <ZPascal>

LABEL application="Integrationtest" \
      description="Base Linux Container Image for the Container Manager Integrationtest" \
      lastModifiedBy="Pascal Zimmermann" \
      lastModifiedOn="2021-10-29"

ADD ./test/integrationtest/image /image

RUN pip install flask && chown -R kubernetes:kubernetes $IMAGE_BASE_DIR && chmod +x /image/app/integrationtest.py

EXPOSE 8080

USER 500