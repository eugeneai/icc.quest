from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, nottest
from lxml import etree

from docx2html import convert
import os.path

from icc.quest.form.core import DOCX2HTMLAdapter
from icc.quest.alchemy.initialize_db import main as create
from icc.quest.alchemy.initialize_db import remove_db
from icc.quest.alchemy import Institution

ECHO = False

INPUT = os.path.abspath('input/query1.docx')
OUTPUT = os.path.abspath('input/query1-{}.html')

DBURI = 'postgresql+psycopg2://postgres:quest312@quest-postgres.isclan.ru/quest-test'
# @SkipTest


class TestBasic:

    def setUp(self):
        pass

    def test_something(self):
        assert 1 + 1 == 2

    def test_convert(self):
        html = convert(INPUT, charset_metadata=True,
                       pretty_print=True, as_tree=True,
                       body=True)
        # print(html)
        o = open(OUTPUT.format('convert'), 'w')
        o.write(etree.tostring(html, pretty_print=True, encoding=str))
        o.close()

    def tearDown(self):
        pass


class TestExt:

    def setUp(self):
        self.a = DOCX2HTMLAdapter(INPUT)

    def out(self, name, tree, stdout=False):
        o = open(OUTPUT.format(name), 'w')
        if isinstance(tree, DOCX2HTMLAdapter):
            s = tree.tostring()
        else:
            s = etree.tostring(tree, encoding=str,
                               pretty_print=True)
        o.write(s)
        o.close()
        if stdout:
            print('OUT {}:{}'.format(name, s))

    def test_adapter(self):
        a = self.a
        a.article()
        tds = a.inputs()
        # print(tds)
        self.out('adapter', a)

    def test_form(self):
        a = self.a
        f = a.as_form()
        self.out('form', f, stdout=False)

    def test_csv_reader(self):
        if os.system != 'nt':
            file_name = "/etc/passwd"
            iter = Institution.load_from_csv(file_name,
                                             delimiter=":", dummy=True)
            for row in iter:
                if row[0] == 'root':
                    return
            else:
                assert True, 'Root not found'
        else:
            print('WARNING: Windows platform test is not implemented')


class TestDatabase:

    def test_create_test_database(self):
        create(URI=DBURI,
               create_db=True, echo=ECHO)

    def test_remove_test_database(self):
        remove_db(URI=DBURI)
