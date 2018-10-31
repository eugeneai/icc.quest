from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, nottest

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
        html = convert(INPUT)
        o = open(OUTPUT, 'w')
        o.write(html)
        o.close()

    def tearDown(self):
        pass
