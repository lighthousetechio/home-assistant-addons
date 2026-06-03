ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
ARG BINARY_VERSION=0.1.7-debug-gc

ENV LANG=C.UTF-8

RUN apk add --no-cache curl ca-certificates

# Map Home Assistant BUILD_ARCH to the binary arch suffix used by openrepo.
RUN set -eu; \
    case "${BUILD_ARCH}" in \
        amd64)   arch=amd64 ;; \
        aarch64) arch=arm64 ;; \
        armv7)   arch=arm7  ;; \
        *) echo "Unsupported BUILD_ARCH: ${BUILD_ARCH}"; exit 1 ;; \
    esac; \
    url="http://openrepo.lighthousetech.io:7376/cloudgateway-generic/client_linux_${arch}_${BINARY_VERSION}"; \
    echo "Downloading ${url}"; \
    curl -fsSL --retry 3 -o /usr/local/bin/cloudgateway "${url}"; \
    chmod +x /usr/local/bin/cloudgateway

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
