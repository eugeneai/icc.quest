from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, nottest
from lxml import etree

from docx2html import convert
import os.path

from icc.quest.form.core import DOCX2HTMLAdapter

INPUT = os.path.abspath('input/query1.docx')
OUTPUT = os.path.abspath('input/query1-{}.html')

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

    def test_adapter(self):
        a = DOCX2HTMLAdapter(INPUT)
        a.article()
        tds = a.inputs()
        print(tds)
        o = open(OUTPUT.format('adapter'), 'w')
        o.write(a.tostring())
        o.close()

    def tearDown(self):
        pass
