'''
	This utility can convert Adobe Flash generated FXG files into SVG files
	To ensure proper conversion of files with this script ensure the following:
	1. Your FXG file source contain only fill types and no lines (can be achieved using convert lines to fill command in flash)
	2. Your top-most flash element is a Graphic type and not a raw drawing (or other element)
	3. You are using python 3.6+
	4. You have installed lxml library using pip
'''

import sys

print('\nTo ensure proper conversion of files with this script ensure the following:');
print('1. Your FXG file source contain only fill types and no lines (can be achieved using convert lines to fill command in flash)');
print('2. Your top-most flash element is a Graphic type and not a raw drawing (or other element)');
print('3. You are using python 3.6+')
print('4. You have installed lxml library using pip\n')

from lxml import etree

input_file = sys.argv[1]

if not input_file:
    # user did not provide a file from terminal command, prompt him to enter now
    input_file = input('Enter file path: ')

if not input_file:
    print('No file provided, Cancelling conversion')
    sys.exit(0)

if not input_file.endswith('.fxg'):
    input_file = input_file + '.fxg'

with open(input_file, 'rb') as f:
    x = etree.parse(f)

root_element = x.getroot()
root_ns = root_element.nsmap[None]

svg = etree.Element(
    'svg',
    viewBox="0 0 "+root_element.attrib['viewWidth']+" "+root_element.attrib['viewHeight'],
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
                    color_data = child.getchildren()[0]
                    try:
                        attrs['fill'] = color_data.attrib['color']
                        attrs['fill-opacity'] = color_data.attrib.get('alpha','1')
                    except:
                        attrs['fill'] = '#000000'
                else:
                    attrs['fill'] = 'none'

                if 'stroke' in child.tag:
                    stroke = child.getchildren()[0]
                    try:
                        attrs['stroke'] = stroke.attrib['color']
                        attrs['stroke-opacity'] = color_data.attrib.get('alpha','1')
                    except:
                        attrs['stroke'] = '#000000'
                    if stroke.attrib.get('weight'):
                        attrs['stroke-weight'] = stroke.attrib['weight']
            root.append(etree.Element('path', **attrs))
    return root

for element in x.iter():
    if 'Definition' in element.tag:
        named_groups[element.attrib['name']] = get_paths_in_element(element)
        key_order.append(element.attrib['name'])

definition_names = named_groups.keys()

if len(definition_names) is 0:
    raise "fxg does not contain any definition tags, please ensure your top level element is a Graphic symbol"

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

output_file = input_file[:-3] + 'svg'
with open(output_file, 'wb') as f:
    f.write(etree.tostring(svg))

print(input_file,'converted to',output_file)
