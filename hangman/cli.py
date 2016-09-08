"""
Make a copy of this file, call it "mycli.py"
Then, adjust the setup.py entry_points to 
"""

import click
from hangman.pics import pics
import subprocess

class HangmanObject(object):
    """
    Interface between the command line and the user
    """
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def echo_red(self, s, **kwargs):
        click.echo(click.style(s, fg='red'))
    def echo_yellow(self, s):
        click.echo(click.style(s, fg='yellow'))
    def echo_white(self, s):
        click.echo(click.style(s, fg='white'))
    def styled_echo(self, s, **kwargs):
        click.echo(click.style(s, **kwargs))
    def stylized_echo(self, s, echo={}, style={}):
        click.echo(click.style(s, **style), **echo)
    def new_line(self):
        click.echo()
    def echo(self, s, **kwargs):
        click.echo(s, **kwargs)
    def clear_screen(self):
        click.clear()
    def prompt(self, s, **kwargs):
        return click.prompt(s, **kwargs)
    def styled_prompt(self, s, style={}, prompt={}):
        return click.prompt(click.style(s, **style), **prompt)
    def pause(self, **kwargs):
        click.pause(**kwargs)

@click.group()
@click.option('-v', '--verbose', default=0, count=True, help="Help to debug your program, add more for more output")
@click.pass_context
def cli(hangman, verbose):
    # Creates the object, only happens once every time it is run
    hangman.obj = HangmanObject(verbose=verbose)

@cli.command('pic')
@click.argument('num_errors', type=int)
@click.option('--color', default="yellow")
@click.pass_obj
def pic(obj, num_errors, color):
    picture = pics[num_errors]
    obj.styled_echo(picture, fg=color)

@cli.command('say')
@click.argument('what', nargs=-1)
@click.pass_obj
def say(obj, what):
    """
    Makes the computer speak out-loud
    Works by calling the system's "say" command (Mac-only)
    If sound is turned off, does nothing
    """
    if not obj.sound: return
    cmds = ['say']
    cmds.extend(what)
    subprocess.run(cmds)

@cli.command('blanks')
@click.argument('answer')
@click.argument('chosen')
@click.option('--clue', default=None)
@click.pass_obj
def blanks(obj, answer, chosen, clue):
    """
    Outputs the answer with blanks, according to chosen
    Color: green for correct, red for incorrect
    """
    # normalize the passed values first
    answer = answer.lower()
    chosen = chosen.lower()

    # Go through each word in the answer
    # and pick the right color
    for word in answer.split(' '):
        for l in range(len(word)):
            letter = word[l].lower()
            if letter in chosen:
                obj.stylized_echo(letter.upper() + ' ', style={'fg':'white'}, echo={'nl': False})
            else:
                obj.stylized_echo('_ ', style={'fg':'yellow'}, echo={'nl': False})
        obj.echo('  ', nl=False)  # space between words

    obj.new_line()

    # output the clue, if provided
    if clue:
        obj.new_line()
        clue = clue.title()
        obj.stylized_echo('Clue: ', echo={'nl':False}, style={'fg':'yellow'})
        obj.echo_white(clue)
    obj.new_line()

    # loop from a to z, counting by integer
    for c in range(ord('a'), ord('z')+1):
        # convert integer into the cooresponding character
        ch = chr(c)
        if ch in chosen:
            if ch in answer:
                color = "green"
            else:
                color = "red"
        else:
            color = "white"
        # output the character, without a new line
        obj.stylized_echo(ch, echo={'nl':False}, style={'fg':color})
    obj.new_line()

def valid_choice(value):
    return len(value) == 1

@cli.command()
@click.pass_obj
def ask_user(obj):
    choice = None
    while not choice:
        choice = obj.styled_prompt("Pick any letter", style={'fg': "yellow"})
        choice = choice.lower()
        if not valid_choice(choice):
            obj.styled_echo("Has to be just one character!", fg="red")
            choice = None
    return choice

@cli.command()
@click.pass_context
def run(hangman):
    """
    Executes the main program loop
    """
    hangman.obj.clear_screen()

    # Get the main program variables that we will use throughout the program
    default_name = "No Name"
    name = hangman.obj.styled_prompt(
        "Enter your name", 
        style={'fg':'yellow'}, 
        prompt={'default':default_name, 'show_default':False}
    )
    hangman.obj.player_name = name
    hangman.obj.sound = not hangman.obj.player_name == default_name
    hangman.obj.player_name = hangman.obj.player_name.title()

    # Say hello to the player
    hangman.invoke(
        say, 
        what=['Greetings, ', hangman.obj.player_name]
    )

    # Get the answer
    hangman.obj.new_line()
    hangman.obj.echo_yellow("Enter the answer (input is hidden so others won't see!)")
    answer = hangman.obj.prompt(' ', hide_input=True)
    hangman.obj.answer = answer

    # Set up the clue
    hangman.obj.new_line()
    clue = hangman.obj.prompt('Clue?', default='', show_default=False)
    if clue:
        hangman.obj.clue = clue
    else:
        hangman.obj.clue = None

    # Set up the counters
    hangman.obj.num_errors = 0
    hangman.obj.remaining = len(list(set([c for c in hangman.obj.answer if c != ' '])))
    hangman.obj.chosen = []

    over = False
    while not over:
        hangman.obj.clear_screen()
        hangman.invoke(
            pic, 
            num_errors=hangman.obj.num_errors
        )
        hangman.obj.new_line()
        hangman.invoke(
            blanks, 
            answer=hangman.obj.answer, 
            chosen="".join(hangman.obj.chosen), 
            clue=hangman.obj.clue
        )
        hangman.obj.new_line()

        if hangman.obj.remaining == 0:
            hangman.obj.echo_yellow('!!!!! YOU WON !!!!!')
            hangman.invoke(
                say, what=["YOU", "WON", "!"]
            )
            hangman.obj.pause(info="")
            hangman.obj.clear_screen()
            over = True
            continue

        choice = hangman.invoke(
            ask_user
        )

        if choice in hangman.obj.chosen:
            hangman.invoke(
                say, 
                what=["What", "are", "you", "doing, ", hangman.obj.player_name, "?"]
            )
            continue

        hangman.invoke(
            say, 
            what=[choice]
        )
        hangman.obj.chosen.append(choice)

        if choice.lower() not in hangman.obj.answer.lower():
            hangman.invoke(
                say, 
                what=['Wrong!']
            )
            hangman.obj.echo_red("WRONG")
            hangman.obj.num_errors += 1

            # check if we lost
            if hangman.obj.num_errors == 6:
                hangman.invoke(
                    say, what=["Ha, ", "you", "lose"]
                )
                hangman.obj.clear()
                hangman.invoke(
                    pic, 
                    num_errors=hangman.obj.num_errors, color="red"
                )
                hangman.obj.new_line()
                hangman.invoke(
                    blanks, 
                    answer=hangman.obj.answer, chosen=hangman.obj.answer
                )
                hangman.obj.pause(info="")
                hangman.obj.clear()
                over = True
        else:
            hangman.invoke(
                say, what=["Yes!"]
            )
            hangman.obj.remaining -= 1





