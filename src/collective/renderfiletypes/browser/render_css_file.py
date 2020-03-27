# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api


class RenderCSSFile(BrowserView):
    def __call__(self):
        self.request.response.setHeader("content-type", "text/css")
        return self.render_stylesheet()

    def render_stylesheet(self):
        mr = api.portal.get_tool("mimetypes_registry")
        ret_string = ""
        for mimetype in mr.mimetypes():
            icon_path = mimetype.icon_path
            if not icon_path.startswith("http"):
                icon_path = "{0}/{1}".format(api.portal.get().absolute_url(), icon_path)

            mimetype_string = """a[type='{mime_type}'] {{
                                    background: url({mime_type_icon_url}) no-repeat 0 50%;
                                    padding-left: 20px;
                                }}
                                """.format(
                mime_type=mimetype.normalized(), mime_type_icon_url=icon_path,
            )

            ret_string += mimetype_string

        return ret_string
