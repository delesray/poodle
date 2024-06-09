FROM mariadb:10.5.25

COPY mariadb_seed.sql /docker-entrypoint-initdb.d/

EXPOSE 3306