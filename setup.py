from distutils.core import setup

setup(
    name='docker_dmc',
    version='0.0.1',
    packages=['CmdDarcMail', 'CmdDarcMail.eaxs', 'CmdDarcMail.xml_help', 'CmdDarcMail.eaxs_json',
              'CmdDarcMail.dir_walker', 'CmdDarcMail.eaxs_helpers'],
    url='',
    license='LICENSE.txt',
    author='Jeremy Gibson',
    author_email='jeremy.gibson@ncdcr.gov',
    description='A modified CmdDarcMail for docker-compose',
    install_requires=[
        "python_jsonschema_objects" >= '0.2.1',
        "lxml" == '3.8.0',
        "ftfy" == '5.0.2',
        "beautifulsoup4" == '4.6.0',
        "PyYAML" == '3.12'
    ]
)
