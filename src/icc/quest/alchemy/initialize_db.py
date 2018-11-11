import os
import sys
import transaction

from sqlalchemy import engine_from_config, create_engine, exc
from sqlalchemy_utils import database_exists, create_database, drop_database

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from .models import (
    DBSession,
    Base,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [ -cv ] \n'
          '(example: "%s development.ini") \n\n'
          'Option -c tries to create database\n'
          'with the same user if it not exists.\n'
          'Option -v add \'echo\' parameter to \n'
          ''
          '' % (cmd, cmd)
          )
    sys.exit(1)


def create_db(engine):
    url = str(engine.url)
    parts = url.split('/')
    pgurl = '/'.join(parts[:-1]+['postgres'])
    dbname = parts[-1]
    print(url, pgurl)
    pgengine = create_engine("postgres://postgres@/postgres")
    conn = engine.connect()
    conn.execute("create database {}".format(dbname))
    conn.close()


def create_all(engine, create_db=False):
    if not database_exists(engine.url) and create_db:
        create_database(engine.url)
    Base.metadata.create_all(engine)

    # try:
    #     Base.metadata.create_all(engine)
    # except exc.OperationalError as e:
    #     import sys
    #     exc_info = sys.exc_info()
    #     msg = str(e.orig)
    #     f1 = msg.find('database')
    #     if f1 >= 0:
    #         f1 += len('database')
    #         f2 = msg.find('does not exist')
    #         if f2 >= 0 and f2 > f1 and _first:
    #             create_db(engine)
    #             return create_all(engine, _first=False)
    #     # raise exc_info[1], None, exc_info[2]
    #     raise


def remove_db(URI):
    """Used for testing only
    """
    drop_database(URI)


def main(argv=sys.argv, URI=None, create_db=False, **kwargs):
    if URI is None:
        if len(argv) < 2:
            usage(argv)
        else:
            config_uri = argv[1]
            setup_logging(config_uri)
            settings = get_appsettings(config_uri)
            if '-v' in argv:
                kwargs["echo"] = True
            engine = engine_from_config(settings, 'sqlalchemy.', **kwargs)
            if '-c' in argv:
                create_db = True
    else:
        engine = create_engine(URI, **kwargs)
    DBSession.configure(bind=engine)
    create_all(engine, create_db=create_db)
    # with transaction.manager:
    #     model = Page(title='Root', body='<p>Root</p>')
    #     DBSession.add(model)
    return engine
