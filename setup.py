from distutils.core import setup
setup(
    name = "My first command-line program",
    version = "0.1",
    description = "description",
    author = "yourname",
    author_email = "",
    keywords = [],
    packages=['cmd', 'gns'],
    entry_points='''
        [console_scripts]
        cmd=cmd.cli:cli
    ''',
    install_requires = ['click'],

    long_description = """
    Your long description here (optional)
    """
)
