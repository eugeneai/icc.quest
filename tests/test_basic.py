from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, nottest
from lxml import etree

from docx2html import convert
import os.path

INPUT = os.path.abspath('input/query1.docx')
OUTPUT = os.path.abspath('input/query1-2.html')

# @SkipTest


class TestBasic:

    def setUp(self):
        pass

    def test_something(self):
        assert 1 + 1 == 2

    def test_convert(self):
        html = convert(INPUT, charset_metadata=True,
                       pretty_print=True, as_tree=True)
        print(html)
        o = open(OUTPUT, 'w')
        o.write(etree.tostring(html, pretty_print=True, encoding=str))
        o.close()

    def tearDown(self):
        pass
