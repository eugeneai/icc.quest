from docx2html import convert
from lxml import etree
import logging
logger = logging.getLogger("icc.quest")


class DOCX2HTML:
    """Clss-adapter of docx document being lazy imported and 
    converted into HTML tree.
    """

    def __init__(self, filename):
        """Constructs the adapter object
        ``filename`` is full path to the file or a stream of docx
        template
        """
        self.filename = filename
        self.tree = None
        self.state = {}

    def lazy_load(self):
        fn = self.filename
        if self.tree is None:
            self.tree = convert(fn, as_tree=True, body=True)

        self.state['loaded'] = True

        return self.tree

    @property
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
        self.state['article'] = True
        return article

    @property
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

            inp = etree.SubElement(td, 'input')
            has_inputs = True
            if value != '':
                inp.set('value', value)

            if 'disabled' in options:
                if value != '':
                    td.text = value
                inp.set('type', 'hidden')

            inp.set('placeholder', defs)
            inp.set('style', 'width:231px;')
            inp.set('name', name)
            inp.set('id', name+'-input')
            cls = inp.get('class', '') + ' query-input'
            inp.set('class', cls.strip())
            inp.set('data-field-name', type_)
            # if 'disabled' in options:
            #     inp.set('disabled', 'disabled')
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
            btn.set('id', 'query-send-button')
            emb.insert(emb.index(tbl)+1, btn)
        self.state['inputs'] = True
        return tds

    @property
    def form(self):
        self.lazy_load()
        tree_copy = self.tostring(pretty_print=False)
        old_tree = etree.fromstring(tree_copy)
        if not self.state.get('inputs', False):
            self.inputs()

        # TODO: select by class 'query-input'
        inputs = self.tree.xpath('//input')

        trq = self.common_parent(inputs)
        assert(trq.tag == 'tr'), "table is too complex"
        tr = trq
        tr.set('data-type-row', 'inputs')
        ptr = tr.getparent()
        th = ptr[0]
        assert(th != tr), "table without header part"

        headers = ptr.xpath(".//tr[1]/td|th")
        # headers = [h.text for h in headers]
        assert(len(headers) == len(inputs))

        labels = [' '.join(h.xpath('./descendant::*/text()')) for h in headers]

        tablep = tr.getparent()
        while tablep.tag != 'table':
            tablep = tablep.getparent()
        parent = tablep.getparent()

        form = etree.Element('form')
        tablep.addnext(form)
        for i, h in zip(inputs, labels):
            self.form_group(form, i, h)

        btn = parent.xpath('.//button[@id="query-send-button"]')
        form.append(btn[0])

        parent.remove(tablep)
        answer = self.tree
        self.tree = old_tree
        return answer

    def form_group(self, form, input, label_text):
        div = etree.SubElement(form, 'div')
        div.set('class', 'form-group')
        input_id = input.get('id')
        label = etree.SubElement(div, 'label', attrib={'for': input_id})
        label.text = label_text
        div.append(input)
        # TODO: Add  <small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
        cls = input.get('class').split()
        if 'form-control' not in cls:
            cls.append('form-control')
        input.set('class', ' '.join(cls))

    def common_parent(self, elements):
        els = elements
        while True:
            if not els:
                return None
            pe = els[0]
            for el in els:
                if (pe != el):
                    break
            else:
                return pe
            newels = []
            for el in els:
                newels.append(el.getparent())
            els = newels

    def tostring(self, tree=None, **kwargs):
        if tree is None:
            self.lazy_load()
            tree = self.tree
        d = {}
        d.update(kwargs)
        d.setdefault("encoding", str)
        d.setdefault("pretty_print", True)
        return etree.tostring(tree, **d)
