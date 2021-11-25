# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
import xbmc, xbmcvfs
from . import addonId


class Binder():
    """Helper class for interlocking slideshow-bgm with the current skin.

    """

    def __init__(self, target=None):
        self.target = target if target else self.find_SlideShow_xml()
        # preserve comments
        self.parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        self.tree = ET.parse(self.target, self.parser)
        self.root = self.tree.getroot()
        self.element = ET.Element('onload')
        self.element.attrib = {'condition': 'System.HasAddon(%s)' % addonId +
                                            ' + ' +
                                            'System.AddonIsEnabled(%s)' % addonId}
        self.element.text = ('RunAddon(%s)' % addonId).strip()

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

    def check_permission(self):
        """Check the write permission for ``SlideShow.xml`` and the enclosing directory

        Returns:
            bool: True if we have the permission, False ohterwise.

        """

        return os.access(self.target, os.W_OK) and \
               os.access(os.path.dirname(self.target), os.W_OK)

    def check_hooked(self):
        """Check current skin's SlideShow.xml is tied to ``slideshow-bgm`` of the current
        skin.

        Technically, check the node of ``<onload condition="System.HasAddon(script.service.slideshow-bgm) +
        System.AddonIsEnabled(script.service.slideshow-bgm)">RunAddon(script.service.slideshow-bgm)</onload>``
        exists in the `SlideShow.xml` file of the current skin.

        Returns:
            bool:  True if it's hooked, False otherwise.

        """

        ret = None
        #: xml.etree.ElementTree.Element: Elements with no subelements will test as ``False``.
        for element in self.root.findall('onload'):
            if element.text.strip() == self.element.text:
                ret = element
                break
            else:
                continue
        return False if ret is None else True

    def insert_tag(self):
        """Insert interlocking tag into `SlideShow.xml` file of the current skin.

        The contents of the tag are ``<onload condition="System.HasAddon(script.service.slideshow-bgm) +
        System.AddonIsEnabled(script.service.slideshow-bgm)">RunAddon(script.service.slideshow-bgm)</onload>``

        Returns:
            bool: True if succeeds, False otherwise.

        """

        self.root.insert(0, self.element)
        self.indent(self.root)
        try:
            self.tree.write(self.target, encoding="utf-8", xml_declaration=True)
        except:
            return False

        return True

    def remove_tag(self):
        """Remove the interlocking tag from `SlideShow.xml` file of the current skin.

        """

        for element in self.root.findall('onload'):
            if element.text.strip() == self.element.text:
                self.root.remove(element)

        self.indent(self.root)
        try:
            self.tree.write(self.target, encoding="utf-8", xml_declaration=True)
        except:
            return False

        return True
