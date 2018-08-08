*document "_DEVEL" and "TOMES_TOOL" as the CLI easter eggs.

*document this:

    # NEEDS DOCUMENTATION. Make sure we specify the correct lxml version in requirements.
    # PS C:\Users\Nitin\Dropbox\TOMES\GitHub\tomes_darcmail> python3 DarcMailCLI.py -a foo .\tests\sample_files\mbox\ -c 100
    Traceback (most recent call last):
	...
    from lxml.ElementInclude import etree
    ModuleNotFoundError: No module named 'lxml.ElementInclude'
    PS C:\Users\Nitin\Dropbox\TOMES\GitHub\tomes_darcmail>
    # see https://github.com/Kozea/WeasyPrint/issues/370
    # definitely mention this and put "https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml" link in documentation.
