"""
Make a copy of this file, call it "mycli.py"
Then, adjust the setup.py entry_points to 
"""

import click
import gns

class Object(object):
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def warn(self, s):
        click.echo(click.style(s, fg='red'))
    def highlight(self, s):
        click.echo(click.style(s, fg='yellow'))
    def plain(self, s):
        click.echo(s)

@click.group()
@click.option('-v', '--verbose', default=0, count=True, help="Help to debug your program, add more for more output")
@click.pass_context
def cli(ctx, verbose):
    # Doesn't do much now, but leave it as boilerplate for when there are global flags n such
    ctx.obj = Object(verbose=verbose)
    if ctx.obj.verbose:
        ctx.obj.warn("VERBOSE")
        if ctx.obj.verbose == 2:
            ctx.obj.highlight("Object contains the following keys:")
            ctx.obj.plain('\t{}'.format(", ".join(["{}={}".format(k, v) for k, v in ctx.obj.__dict__.items()])))

@cli.command()
@click.pass_obj
def hello(obj):
    """
    Hello world!
    """
    click.echo(click.style("Hello world!", fg='green'))
    pass

@cli.command()
@click.argument('what', nargs=-1)
@click.pass_obj
def say(obj, what):
    """
    Makes the computer speak out loud
    """
    import subprocess
    if obj.verbose == 2:
        obj.plain("Running say")
        obj.plain(what)
    badwords = gns.config.vulgar.badwords.split(" ")
    for badword in badwords:
        if badword in " ".join(what):
            obj.warn("I am not going to say that!")
            return
    cmds = ['say']
    cmds.extend(what)
    subprocess.run(cmds)
