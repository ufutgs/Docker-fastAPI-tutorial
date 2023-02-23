FROM mysql:5.7
LABEL description="Test database."
ENV MYSQL_DATABASE test_DB
#Check out docker entry point for further configuration :
# https://github.com/docker-library/mysql
COPY ./init-scripts/ /docker-entrypoint-initdb.d/