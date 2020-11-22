# -*- coding: utf-8 -*-
"""Hook slideshow-BGM addon up to the current skin

Technically, insert ``<onload> RunAddon(script.slideshow-BGM) </onload>`` into
the beginning of `SlideShow.xml` file of the current skin.

Notes:
    If you are using the default skin(as of Leia, ``estuary``), you have to
    run this script as root because of permission issue.

"""

from __future__ import absolute_import
import os
import xml.etree.ElementTree as ET
import xbmc


def indent(elem, level=0):
    """Arrange indentations of xml nodes.

    Copied from <http://effbot.org/zone/element-lib.htm#prettyprint>_
    Args:
        elem (:obj:`xml.etree.ElementTree.Element`): top element to indent
        level (int): indentation level(default 0)

    """
    i = os.linesep + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

            
def find_slideshow_xml():
    """Locate ``SlideShow.xml`` file of the current skin.

    Returns:
        str: The path of ``SlideShow.xml`` file.

    """
    name = 'SlideShow.xml'
    skin_dir = xbmc.translatePath('special://skin')
    for root, dirs, files in os.walk(skin_dir):
        if name in files:
            return os.path.join(root, name)


if __name__ == "__main__":
    xml_file = find_slideshow_xml()
    tree = ET.parse(xml_file)
    root = tree.getroot()
    element = ET.Element('onload')
    element.text = 'RunAddon(script.slideshow-BGM)'

    root.insert(0, element)
    indent(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
