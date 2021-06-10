# -*- coding: utf-8 -*-
from plone import api
from plone.outputfilters.browser.resolveuid import uuidToObject
from bs4 import BeautifulSoup
from collective.renderfiletypes.interfaces import ICollectiveRenderfiletypesLayer
from plone.outputfilters.interfaces import IFilter
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.parse import urlunsplit
from zope.interface import implementer
from collective.renderfiletypes.utils import human_readable_size


import re
import six

from zope.i18n import translate

appendix_re = re.compile("^(.*)([?#].*)$")
resolveuid_re = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")

ENABLED_TYPES = "File"


@implementer(IFilter)
class RenderFileTypesFilter(object):
    singleton_tags = set(
        [
            "area",
            "base",
            "basefont",
            "br",
            "col",
            "command",
            "embed",
            "frame",
            "hr",
            "img",
            "input",
            "isindex",
            "keygen",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ]
    )

    filesizes = {
        'KB': 'KiloBytes',
        'MB': 'MegaBytes',
        'GB': 'GigaBytes'
    }

    # This should go before the resolveUID filter
    order = 700

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_enabled(self):
        return ICollectiveRenderfiletypesLayer.providedBy(self.request)

    def __call__(self, data):
        data = re.sub(r"<([^<>\s]+?)\s*/>", self._shorttag_replace, data)
        soup = BeautifulSoup(safe_unicode(data), "html.parser")

        for elem in soup.find_all(["a"]):
            attributes = elem.attrs
            href = attributes.get("href")
            file_type_information = None
            if attributes.get("data-linktype", "") == "external":
                file_type_information = self.get_file_type_from_url(href)
            else:
                # an 'a' anchor element has no href
                if not href:
                    continue
                url_parts = urlsplit(href)
                # we are only interested in path and beyond /foo/bar?x=2#abc
                path_parts = urlunsplit(["", ""] + list(url_parts[2:]))
                if (
                    not href.startswith("mailto<")
                    and not href.startswith("mailto:")
                    and not href.startswith("tel:")
                    and not href.startswith("#")
                ):
                    obj, subpath, appendix = self.resolve_link(path_parts)
                    file_type_information = None
                    if obj is not None:
                        file_type_information = self.get_file_type_from_object(obj)

            if file_type_information is not None:
                file_type = file_type_information.get("file_type")
                file_size = file_type_information.get("file_size")
                human_size = human_readable_size(file_size)
                
                human_size_number, human_size_text = human_size.split(' ')
                human_size_longtext = self.filesizes[human_size_text]
                mimetype_registry = self.context.mimetypes_registry
                if mimetype_registry.lookup(file_type):
                    icon_url = mimetype_registry.lookup(file_type)[
                        0
                    ].icon_path
                    contenttype = mimetype_registry.lookup(file_type)[
                        0
                    ].name()
                else:
                    icon_url = mimetype_registry.lookup("application/octet-stream")[
                        0
                    ].icon_path
                    contenttype = mimetype_registry.lookup("application/octet-stream")[
                        0
                    ].name

                tr = translate(contenttype, 'plone', target_language='es')

                file_type_image = """
                <img src="{url}" alt="formato {contenttype}" title="archivo {contenttype}" />
                """.format(
                    contenttype=tr,
                    url=icon_url,
                )
                elem.insert(0,BeautifulSoup(file_type_image, "html.parser"))
                
                file_type_html = """
                <span class="type">
                ({human_size_number} <abbr title="{human_size_longtext}">{human_size_text}</abbr>)
                </span>
                """.format(
                    human_size_number=human_size_number,
                    human_size_longtext=human_size_longtext,
                    human_size_text=human_size_text,
                )
                elem.append(BeautifulSoup(file_type_html, "html.parser"))
                attributes["type"] = file_type
            else:
                if 'target' in attributes:
                    target = attributes.get('target')
                    help_text = "Abre ventana nueva"
                    if attributes.get("data-linktype", "") == "external":
                        if target == '_blank' or target == '_new':
                            attributes["class"] = 'external_link_blank_icon'
                        else:
                            attributes["class"] = 'external_link_icon'
                    elif attributes.get("data-linktype", "") == "internal":
                        if target == '_blank' or target == '_new':
                            attributes["class"] = 'internal_link_blank'
                else:
                    if attributes.get("data-linktype", "") == "external":
                        help_text = "Web externa"
                        attributes["class"] = 'external_link_icon'
                    else:
                        attributes["class"] = None

                if attributes.get("class", None):
                    icon_url = "{0}/++resource++mimetype.icons/{1}".format(api.portal.get().absolute_url(), attributes["class"] + '.png')
                    file_type_image = """
                    <img src="{url}" alt="{help_text}" title="{help_text}" />
                    """.format(url=icon_url, help_text=help_text)
                    elem.insert(0,BeautifulSoup(file_type_image, "html.parser"))

        return six.text_type(soup)

    def resolve_link(self, href):
        obj = None
        subpath = href
        appendix = ""

        # preserve querystring and/or appendix
        match = appendix_re.match(href)
        if match is not None:
            subpath, appendix = match.groups()

        # resolve UIDs
        match = resolveuid_re.match(subpath)
        if match is not None:
            uid, _subpath = match.groups()
            obj = self.lookup_uid(uid)
            if obj is not None:
                subpath = _subpath

        return obj, subpath, appendix

    def get_file_type_from_object(self, obj):
        if obj.portal_type in ENABLED_TYPES:
            mimetype = self.mimetype_by_extension(obj.file.filename)
            icon_path = "{0}/{1}".format(api.portal.get().absolute_url(), mimetype.icon_path)
            return {
                "file_type": obj.file.contentType,
                "file_size": obj.file.size,
                "file_filename": obj.file.filename,
                "icon_path": icon_path,
            }
        return None

    def get_file_type_from_url(self, url):
        path, filename = url.rsplit("/", 1)
        mimetype = self.mimetype_by_extension(filename)
        if mimetype:
            return {
                "file_type": mimetype and mimetype.normalized() or "Unkown format",
                "file_size": "Unkown size",
                "file_filename": filename,
            }
        else:
            return None

    def _shorttag_replace(self, match):
        tag = match.group(1)
        if tag in self.singleton_tags:
            return "<" + tag + " />"
        else:
            return "<" + tag + "></" + tag + ">"

    def lookup_uid(self, uid):
        return uuidToObject(uid)

    def mimetype_name(self, mimetype):
        mr = api.portal.get_tool("mimetypes_registry")
        mimetype_objects = mr.lookup(mimetype)
        if mimetype_objects:
            return mimetype_objects[0].name()
        return ""

    def mimetype_by_extension(self, filename):
        mr = api.portal.get_tool("mimetypes_registry")
        return mr.lookupExtension(filename)

    def get_file_type_img_url(self, url):
        path, filename = url.rsplit("/", 1)
        mimetype = self.mimetype_by_extension(filename)
        return mimetype