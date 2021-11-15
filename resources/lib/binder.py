# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
import xbmc, xbmcvfs
from . import addon, addonId

class Binder(target=Binder.find_SlideShow_xml()):
    """Helper class used to tie slideshow-BGM addon to the current skin.

    """

    def __init__(self):
        self.target = target
        self.parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))  # preserve comments
        self.tree = ET.parse(self.target, self.parser)
        self.root = self.tree.getroot()
        self.element = ET.Element('onload')
        self.element.attrib = {'condition': 'System.HasAddon(%s)' % addonId + ' + ' + 'System.AddonIsEnabled(%s)' % addonId}
        self.element.text = 'RunAddon(%s)' % addonId
        
    def indent(self, elem, level=0):
        """Arrange indentations of a xml tree.

        Copied from <http://effbot.org/zone/element-lib.htm#prettyprint>_

        Args:
            elem (:obj:`xml.etree.ElementTree.Element`): top element to indent
            level (int): indentation level(default 0)

        """

        i = os.linesep + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    @staticmethod
    def find_SlideShow_xml():
        """Locate ``SlideShow.xml`` file of the current skin.

        Returns:
            str: The path of ``SlideShow.xml`` file.

        """

        fname = 'SlideShow.xml'
        path = ''
        skin_dir = xbmcvfs.translatePath('special://skin')
        for root, dirs, files in os.walk(skin_dir):
            if fname in files:
                path = os.path.join(root, fname)
                break

        return path

    def check_hooked(self):
        """Check current skin's SlideShow.xml is tied to ``slideshow-BGM`` of the current
        skin.

        Technically, check ``<onload  condition="System.HasAddon(script.slideshow-BGM) + System.AddonIsEnabled(script.slideshow-BGM)">
        RunAddon(script.slideshow-BGM)</onload>`` node exists in the `SlideShow.xml` file of the current skin.

        Returns:
            tag(:class:`xml.etree.ElementTree.Element`):  tag if it's hooked, None otherwise.

        """

        for element in self.root.findall('onload'):
            if element.text.strip() == 'RunAddon(script.slideshow-BGM)':
                return element
            else:
                return None

    def insert_tag(self):
        """Insert tag ``<onload condition="System.HasAddon(script.slideshow-BGM) + System.AddonIsEnabled(script.slideshow-BGM)">
        RunAddon(script.slideshow-BGM)</onload>`` into `SlideShow.xml` file of the current skin.

        Returns:
            bool: True if suceeds, False otherwise.

        """

        self.root.insert(0, self.element)
        self.indent(self.root)
        if self.tree.write(self.target, encoding="utf-8", xml_declaration=True):
            return True
        else:
            return False

    def remove_tag(self):
        """Remove tag ``<onload condition="System.HasAddon(script.slideshow-BGM) + System.AddonIsEnabled(script.slideshow-BGM)"> 
        RunAddon(script.slideshow-BGM) </onload>`` from `SlideShow.xml` file of the current skin.

        Returns:
            bool: True if suceeds, False otherwise.

        """

        for element in self.root.findall('onload'):
            if element.text.strip() == 'RunAddon(script.slideshow-BGM)':
                self.root.remove(element)
                self.indent(self.root)
                return self.tree.write(self.target, encoding="utf-8", xml_declaration=True)
            else:
                return None
