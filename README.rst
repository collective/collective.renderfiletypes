.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==========================
collective.renderfiletypes
==========================

This product adds a new filter to Plone to render mimetype icons before any
link added in the content.

It gets the mimetype icon from Plone's own MimeTypes Registry. You can override the styling
overriding the CSS file. The CSS file is built dynamicaly from the MimeTypes Registry itself
so it's a browser page (look at browser folder).


Installation
------------

Install collective.renderfiletypes by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.renderfiletypes


and then running ``bin/buildout``

Go to Addons Control Panel and install it there.


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.renderfiletypes/issues
- Source Code: https://github.com/collective/collective.renderfiletypes


Support
-------

If you are having issues, please let us know filing an issue in Github.


License
-------

The project is licensed under the GPLv2.
