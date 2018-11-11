import os
import sys
import transaction

from sqlalchemy import engine_from_config, create_engine, exc
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.orm import sessionmaker

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from .models import (
    DBSession,
    Base,
    InstitutionType,
    Institution
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


SESSION = None


def fill_in_basics():
    sess = SESSION()

    inst_type = sess.query(InstitutionType).first()
    if inst_type is None:  # Suppose Database is empty
        sess.add_all([
            InstitutionType(
                title="Муниципальное казенное дошкольное образовательное учреждение",
                abbreviation="МБДОУ"),
            InstitutionType(
                title="Муниципальное казенное образовательное учреждение (средняя общеобразовательная школа)",
                abbreviation="МБОУ СОШ"),
            InstitutionType(
                title="Муниципальное казенное образовательное учреждение (гимназия)",
                abbreviation="МБОУ ГИМНАЗИЯ"),
            InstitutionType(
                title="Муниципальное казенное образовательное учреждение (лицей)",
                abbreviation="МБОУ ЛИЦЕЙ")
        ])
        sess.commit()


def remove_db(URI):
    """Used for testing only
    """
    drop_database(URI)


def main(argv=sys.argv, URI=None, create_db=False, **kwargs):
    global SESSION
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

    SESSION = sessionmaker(bind=engine)
    fill_in_basics()

    return engine
