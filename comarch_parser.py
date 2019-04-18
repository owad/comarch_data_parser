#!./venv/bin/python

from lxml import etree
from text_unidecode import unidecode

input = etree.parse('input.xml').getroot()

root = etree.Element("PRZELEWY")
output = etree.ElementTree(root)

def find(element, tag):
    children = element.getchildren()
    for child in children:
        if child.tag.endswith(tag):
            return child
        find(child, tag)

def find_by_path(root, tag_path):
    """
    Path example: "CdtTrfTxInf.CdtrAcct.Id.Othr.Id
    """
    for tag in tag_path.split('.'):
        root = find(root, tag)
    
    return root

for PmtInf in input.getchildren()[0].getchildren():
    if not PmtInf.tag.endswith('PmtInf'):
        continue

    entry = etree.SubElement(root, "PRZELEW")

    dataMap = [
        # name, path, default
        ('referencje', None, ''),
        ('rach_obc', 'DbtrAcct.Id.IBAN', None),
        ('bank', None, ''),
        ('rachunek', 'CdtTrfTxInf.CdtrAcct.Id.Othr.Id', None),
        ('data', None, ''),
        ('nazwa1', 'CdtTrfTxInf.Cdtr.Nm', None),
        ('nazwa2', 'CdtTrfTxInf.Cdtr.PstlAdr.AdrLine', None),
        ('kwota', 'CdtTrfTxInf.Amt.InstdAmt', None),
        # ('waluta', 'CdtTrfTxInf.Amt.InstdAmt.Ccy', None),
        ('kraj', None, 'PL'),
    ]

    for name, path, default in dataMap:
        try:
            if path is None:
                text = default
            else:
                found = find_by_path(PmtInf, path)
                text = unidecode(found.text)
    
        except AttributeError as e:
            raise Exception(
                'Value for "{}" not found on path "{}"'.format(
                    name,
                    path,
                )
            )

        element = etree.SubElement(entry, name)
        element.text = text

        if name == 'kwota':  # add currency
            element = etree.SubElement(entry, 'waluta')
            element.text = found.attrib.get('Ccy')    

with open('output.xml', 'wb') as output_file:
    output_str = etree.tostring(output)
    output_file.write(output_str)
