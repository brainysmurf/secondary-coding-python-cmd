"""
Hangman game, for instructional purposes
"""

import click
from hangman.pics import pics
import subprocess
import time

class HangmanObject(object):
    """
    HangmanObject is the 'obj' in this program, and is passed to the functions
    Interface between the command line and the user
    """
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def echo_red(self, s, **kwargs):
        click.echo(click.style(s, fg='red'))
    def echo_green(self, s, **kwargs):
        click.echo(click.style(s, fg='green'))
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
    def is_solved(self):
        """
        In order to determine if the player has won
        We use some math, specifically a set operation
        Spaces do not count for the 'answer', so we have to remove them with the String.replace function
        """
        return (set(self.answer.lower().replace(' ', '')) - set(self.chosen.lower())) == set()

@click.group()
@click.option('-v', '--verbose', default=0, count=True, help="Help to debug your program, add more for more output")
@click.option('-ns', '--nosound', default=True, is_flag=True, help="Toggle the sound, default is on")
@click.pass_context
def cli(hangman, verbose, nosound):
    # Creates the object, only happens once every time it is run
    hangman.obj = HangmanObject(verbose=verbose, sound=nosound)

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
    if not obj.sound:
        time.sleep(0.2)  # slight delay
        return
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
    width_count = 0
    max_width, _ = click.get_terminal_size()
    for word in answer.split(' '):
        width_count += (len(word) + 1) * 2
        if width_count > max_width:
            obj.new_line()
            width_count = (len(word) + 1) * 2
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
        if choice == 'debug':
            # special operation to go into the debugger
            from IPython import embed;embed()
            choice = None
            continue
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
    hangman.obj.chosen = ''

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
            chosen=hangman.obj.chosen,
            clue=hangman.obj.clue
        )
        hangman.obj.new_line()

        if hangman.obj.is_solved():
            hangman.obj.echo_yellow('!!!!! YOU WON !!!!!')
            hangman.invoke(
                say, what=hangman.obj.answer.split(' ')
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
        hangman.obj.chosen += choice

        if choice.lower() not in hangman.obj.answer.lower():
            hangman.obj.echo_red('No')
            hangman.invoke(
                say, 
                what=['No!']
            )
            hangman.obj.num_errors += 1

            if hangman.obj.num_errors == 5:
                hangman.invoke(
                    say, what=["Careful..."]
                )

            # check if we lost
            if hangman.obj.num_errors == 6:
                hangman.obj.echo_red("HA!")
                hangman.invoke(
                    say, what=["Ha, ", "you", "lose"]
                )
                hangman.obj.clear_screen()
                hangman.invoke(
                    pic, 
                    num_errors=hangman.obj.num_errors, color="red"
                )
                hangman.obj.new_line()
                hangman.obj.echo("Correct:")
                hangman.obj.new_line()
                hangman.invoke(
                    blanks, 
                    answer=hangman.obj.answer, chosen=hangman.obj.answer
                )
                hangman.obj.new_line()
                hangman.obj.new_line()
                hangman.obj.echo("Your plays:")
                hangman.invoke(
                    blanks, 
                    answer=hangman.obj.answer, chosen=hangman.obj.chosen
                )                
                hangman.obj.pause(info="")
                hangman.obj.clear_screen()
                over = True
        else:
            hangman.obj.echo_green("Yes!")
            hangman.invoke(
                say, what=["Yes!"]
            )





