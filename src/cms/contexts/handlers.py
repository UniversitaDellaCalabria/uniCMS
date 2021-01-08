
from . models import WebPath


class BaseContentHandler(object):
    template = "default_template.html"

    def __init__(self, path:str,
                 webpath:WebPath = None,
                 template_fname:str = None,
                 **kwargs
            ): # pragma: no cover
        """
        Checks if a path belongs to a CMS specialized application
        :type webpath: cmscontext.model.WebPath
        :type path: String
        :type template_fname: String.
        :param webpath: the context where it should belong to.
                        Its fullpath should be a kind of prefix of
                        settings.CMS_PUBLICATION_URLPATH_REGEXP
        :param path:
        :param template: If present override the default one.
                         its content would be the Template() object
                         string argument

                         template = Template(open(template_fname).read())
                         context = Context({"my_name": "Adrian"})
                         template.render(context)
        :return: render the HTML page
        """
        self.webpath = webpath
        self.path = path
        self.template = template_fname or self.template
        for k,v in kwargs.items():
            setattr(self, k, v)

    def match(self) -> bool: # pragma: no cover
        """
        check if settings.CMS_PUBLICATION_URLPATH_REGEXP matches
        with the given path. Return True or False
        """
        raise NotImplementedError()

    def get(self): # pragma: no cover
        """
            returns a queryset with the results
        """
        raise NotImplementedError()

    def url(self): # pragma: no cover
        """
            returns an absolute url to the render view
        """
        raise NotImplementedError()

    def as_view(self): # pragma: no cover
        """
            get the template configured for this resources (self.template)
            open
            returns a rendered page
        """
        raise NotImplementedError()
