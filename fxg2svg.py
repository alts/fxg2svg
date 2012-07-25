from lxml import etree

with open('example.fxg', 'rb') as f:
    x = etree.parse(f)

root_ns = x.getroot().nsmap[None]

svg = etree.Element(
    'svg',
    width="8cm",
    height="8cm",
    viewBox="0 0 800 800",
    xmlns="http://www.w3.org/2000/svg",
    version="1.1"
)

named_groups = {}
key_order = []

def get_paths_in_element(el):
    root = etree.Element('g')
    for element in el.iter():
        if 'Path' in element.tag:
            attrs = {'d': element.attrib['data']}
            for child in element.getchildren():
                if 'fill' in child.tag:
                    attrs['fill'] = child.getchildren()[0].attrib['color']
                else:
                    attrs['fill'] = 'none'

                if 'stroke' in child.tag:
                    stroke = child.getchildren()[0]
                    attrs['stroke'] = stroke.attrib['color']
                    if stroke.attrib.get('weight'):
                        attrs['stroke-weight'] = stroke.attrib['weight']
            root.append(etree.Element('path', **attrs))
    return root

for element in x.iter():
    if 'Definition' in element.tag:
        named_groups[element.attrib['name']] = get_paths_in_element(element)
        key_order.append(element.attrib['name'])

definition_names = named_groups.keys()
for element in x.iter():
    tag = element.tag.split('}')[-1]
    if tag in definition_names:
        root = etree.Element('g')
        parent = root

        children = element.getchildren()
        if children:
            for el in element.iter():
                if 'Matrix' in el.tag:
                    attrs = el.attrib
                    parent = etree.SubElement(
                        parent,
                        'g',
                        transform='matrix({0},{1},{2},{3},{4},{5})'.format(
                            attrs.get('a', 0),
                            attrs.get('b', 0),
                            attrs.get('c', 0),
                            attrs.get('d', 0),
                            attrs.get('tx', 0),
                            attrs.get('ty', 0)
                        )
                    )
        else:
            attrs = element.attrib
            if 'x' in attrs or 'y' in attrs:
                parent = etree.SubElement(
                    parent,
                    'g',
                    transform='translate({0},{1})'.format(
                        attrs.get('x', 0),
                        attrs.get('y', 0)
                    )
                )
            if 'scaleX' in attrs or 'scaleY' in attrs:
                parent = etree.SubElement(
                    parent,
                    'g',
                    transform='scale({0},{1})'.format(
                        attrs.get('scaleX', 0),
                        attrs.get('scaleY', 0)
                    )
                )
            if 'rotation' in attrs:
                parent = etree.SubElement(
                    parent,
                    'g',
                    transform='rotate({0})'.format(
                        attrs.get('rotation', 0)
                    )
                )
        parent.append(named_groups[tag])
        svg.append(root)

print etree.tostring(svg)
