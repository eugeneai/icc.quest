# Web application for organizing a very fast questionaries and their reports

The web-application allows an organization to rapidly organize surveys among subdivision and aggregate obtained information in simple reports.

## Docker images

Install new docker network.

```bash
docker network create --ipv6 --subnet=2001:db8:XXXX:Y00Z::/64 UUUU-network
```
XXXX, Y,Z - Hexadecimal numbers of network wit prefix, e.g. /64.

### PostgreSQL server

1. Install server in the network
```shell
docker volume create quest-pgdata  # A Host based volume of the data to be stored in
docker run --name quest-postgres --ip6 2001:db8:XXXX:Y00Z::2 --network=UUUU-network -v quest-pgdata:/var/lib/postgresql/data/pgdata -e POSTGRES_PASSWORD=<postgres-password> -d postgres:11.1
```

Save postgres password to install it later in the application.

2. create DNS record with address of the server.
```text
2001:db8:XXXX:Y00Z::2 postgres.example.com
```

or use container linking with `<TODO>`.

### Application
```sell
```

## SQLalchemy Refereces

Tutorial: https://docs.sqlalchemy.org/en/latest/orm/tutorial.html

Column types: https://docs.sqlalchemy.org/en/latest/core/type_basics.html

Pyramid SQLalchemy outline: https://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/databases.html

Short tutorial: https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
