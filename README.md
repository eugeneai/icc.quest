# Web application for organizing a very fast questionaries and their reports

The web-application allows an organization to rapidly organize surveys among subdivision and aggregate obtained information in simple reports.

## Docker images

Install new docker network.

```bash
docker network create --ipv6 --subnet=2001:db8:XXXX:Y00Z::/64 quest-network
```
XXXX, Y,Z - Hexadecimal numbers of network wit prefix, e.g. /64.

### PostgreSQL server

1. Install server in the network
```shell
docker volume create quest-pgdata  # A Host based volume of the data to be stored in
docker run --name quest-postgres --ip6 2001:db8:XXXX:Y00Z::2 --network=quest-network -v quest-pgdata:/var/lib/postgresql/data/pgdata -e POSTGRES_PASSWORD=<postgres-password> -d postgres:11.1
```

Save postgres password to install it later in the application.

2. create DNS record with address of the server.
```text
2001:db8:XXXX:Y00Z::2 postgres.example.com
```

or use container linking with `<TODO>`.

#### Optional install pgAdmin4, the WEB application for administering PostgreSQL servers

```shell
docker pull dpage/pgadmin4
docker run -p 8089:80  --name=pgadmin-quest --network=quest-network  --add-host=postgres:2001:db8:XXXX:Y00Z::2 -e "PGADMIN_DEFAULT_EMAIL=user@example.com" -e  "PGADMIN_DEFAULT_PASSWORD=SuperSecret" --ip6 2001:db8:XXXX:Y00Z::80 -e PGADMIN_ENABLE_TLS=True -p 8443:443 -d --restart=always dpage/pgadmin4
```

So, in the login screen at `http://yoursite.example.com:8089` one must login with the provided `user@example.com` and the password.
The pgAdmin4 user interface served with the unencrypted protocol `HTTP` and password will be clearly seen.

Web-based administrator console `phpPgAdmin` does not support postgresl-11.1

### Application inside DOCKER
```sell
```

### Application running from command-line

#### Initialization of the database

Go to project package folder (`icc.quest`), run

```shell
init_quest_db icc.quest.ini
```

You might need to edit `icc.quest.ini` first to set up database connection URI in `sqlalchemy.url` in `[app:main]` section.

## SQLalchemy Refereces

Tutorial: https://docs.sqlalchemy.org/en/latest/orm/tutorial.html

Column types: https://docs.sqlalchemy.org/en/latest/core/type_basics.html

Pyramid SQLalchemy outline: https://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/databases.html

Short tutorial: https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
