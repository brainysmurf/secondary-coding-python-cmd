from distutils.core import setup
setup(
    name = "Speaking Hangman",
    version = "0.5",
    description = "Do hangman, the cmdline way",
    author = "Adam Morris",
    author_email = "",
    keywords = [],
    packages=['hangman'],
    entry_points='''
        [console_scripts]
        hangman=hangman.cli:cli
    ''',
    install_requires = ['click'],

    long_description = """
    A way of doing the hangman game through the command line
    """
)
