from docx2html import convert
from lxml import etree
import logging
logger = logging.getLogger("icc.quest")


class DOCX2HTMLAdapter:
    """Clss-adapter of docx document being laizily imported and
    converted into HTML tree.
    """

    def __init__(self, filename):
        """Constructs the adapter object
        ``filename`` is full path to the file or a stream of docx
        tmeplate
        """
        self.filename = filename
        self.tree = None

    def lazy_load(self):
        fn = self.filename
        if self.tree is None:
            self.tree = convert(fn, as_tree=True, body=True)
        return self.tree

    def article(self):
        t = self.lazy_load()
        body = t.xpath("//body")[0]
        bchl = t.xpath("//body/*")
        article = etree.SubElement(body, 'article',
                                   {'id': 'main-document',
                                    'property': "oa:hasBody",
                                    'typeof': "schema:Article foaf:Document curr:WorkingProgram",
                                    'resource': "#fill-in-form"
                                    })
        for el in bchl:
            article.append(el)
        return article

    def inputs(self):
        tds = self.tree.xpath("//td[re:match(text(), '^:[a-zA-Z0-9_]+')]",
                              namespaces={"re": "http://exslt.org/regular-expressions"})
        logger.debug('TDS: {}'.format(tds))
        has_inputs = False
        for td in tds:
            defs = td.text  # definitions
            td.text = None
            os_ = (defs+':::').split(':')[1:]
            name, type_ = os_[:2]
            options = set(os_[2:])
            options.discard('')
            value = ''
            if name == 'school':
                value = 'МКУ ЦБ № 4'

            if 'disabled' not in options:
                inp = etree.SubElement(td, 'input')
                has_inputs = True
                if value != '':
                    inp.set('value', value)
            else:
                if value != '':
                    td.text = value
                    continue
            inp.set('placeholder', defs)
            inp.set('style', 'width:231px;')
            inp.set('name', name)
            inp.set('data-field-name', type_)
            if 'disabled' in options:
                inp.set('disabled', 'disabled')
            if 'hidden' in options:
                inp: set('type', 'hidden')
            else:
                inp.set('type', 'text')
        if has_inputs:
            tbl = self.tree.xpath('//table')[0]
            emb = tbl.getparent()
            btn = etree.Element('button')
            btn.text = 'Отправить'
            btn.set('class', "btn btn-primary")
            emb.insert(emb.index(tbl)+1, btn)
        return tds

    def tostring(self, **kwargs):
        d = {}
        d.update(kwargs)
        d.setdefault("encoding", str)
        d.setdefault("pretty_print", True)
        return etree.tostring(self.tree, **d)
