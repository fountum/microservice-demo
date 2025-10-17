FROM mysql:latest
COPY --chown=mysql:mysql ./setup.sql /docker-entrypoint-initdb.d/
EXPOSE 3306