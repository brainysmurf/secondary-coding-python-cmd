"""
Hangman game, for instructional purposes
"""

from hangman.pics import pics   # pics: lets us use the pics defined in the other file
import subprocess               # subprocess: Gives us the 'say' command
import time                     # time: let's us delay the action briefly

import click                    # click: provides tools that makes input and output much easier for the programmer
"""
Click is a framework provided by an open source group
http://click.pocoo.org/
We use it to interact with the user and 
    to ouput stuff to the screen
The next 10 lines defines more descriptive variables for
    the click functions that we use
"""
output_to_screen  = click.echo
stylize_string    = click.style
prompt_user       = click.prompt
wait_for_any_key  = click.pause
pass_hangman      = click.pass_context
form_group        = click.group
make_command      = click.command
add_argument      = click.argument
add_option        = click.option
add_argument      = click.argument


class HangmanObject(object):
    """
    HangmanObject is the 'obj' in this program, and is passed to the functions
    Provides functions that:
       * output to screen
       * gets input from ask_user
    """
    def __init__(self, verbose, sound):
        """
        Called at object creation
        """
        self.verbose = verbose   # note: verbose is not currently used for anything
        self.sound = sound       # sound or no sound?
    def echo(self, s, **kwargs):
        output_to_screen(s, **kwargs)
    def echo_red(self, s, **kwargs):
        output_to_screen(stylize_string(s, fg='red'), **kwargs)
    def echo_green(self, s, **kwargs):
        output_to_screen(stylize_string(s, fg='green'), **kwargs)
    def echo_yellow(self, s):
        output_to_screen(stylize_string(s, fg='yellow'))
    def echo_white(self, s):
        output_to_screen(stylize_string(s, fg='white'))
    def styled_echo(self, s, **kwargs):
        output_to_screen(stylize_string(s, **kwargs))
    def stylized_echo(self, s, echo={}, style={}):
        output_to_screen(stylize_string(s, **style), **echo)
    def new_line(self):
        output_to_screen()
    def clear_screen(self):
        click.clear()
    def prompt(self, s, **kwargs):
        return prompt_user(s, **kwargs)
    def styled_prompt(self, s, style={}, prompt={}):
        return prompt_user(stylize_string(s, **style), **prompt)
    def pause(self, **kwargs):
        wait_for_any_key(**kwargs)
    def is_solved(self):
        """
        In order to determine if the player has won
        We use some math, specifically a set operation
        Spaces do not count for the 'answer', so we have to remove them with the String.replace function
        """
        answer = self.answer.lower().replace(' ', '')
        chosen = self.chosen.lower()
        answer_set = set(answer)
        chosen_set = set(chosen)
        return (answer_set - chosen_set) == set()

@form_group()
@add_option('-v', '--verbose', default=0, count=True, help="Help to debug your program, add more for more output")
@add_option('-ns', '--nosound', default=True, is_flag=True, help="Toggle the sound, default is on")
@pass_hangman
def cli(hangman, verbose, nosound):
    """
    This function is a 'magic' function
    It gets called everytime the program starts
    """
    # Creates the hangman object, store it in the 'obj' of our game
    hangman.obj = HangmanObject(verbose=verbose, sound=nosound)

@cli.command('pic')
@add_argument('num_errors', type=int)
@add_option('--color', default="yellow")
@pass_hangman
def pic(hangman, num_errors, color):
    picture = pics[num_errors]
    hangman.obj.styled_echo(picture, fg=color)

@cli.command('say')
@add_argument('what', nargs=-1)
@pass_hangman
def say(hangman, what):
    """
    Makes the computer speak out-loud
    Works by calling the system's "say" command (Mac-only)
    If sound is turned off, does nothing
    """
    if not hangman.obj.sound:
        time.sleep(0.2)  # slight delay
        return
    cmds = ['say']
    cmds.extend(what)
    subprocess.run(cmds)

@cli.command('blanks')
@add_argument('answer')
@add_argument('chosen')
@add_option('--clue', default=None)
@pass_hangman
def blanks(hangman, answer, chosen, clue):
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
            hangman.obj.new_line()
            width_count = (len(word) + 1) * 2
        for l in range(len(word)):
            letter = word[l].lower()
            if letter in chosen:
                hangman.obj.stylized_echo(letter.upper() + ' ', style={'fg':'white'}, echo={'nl': False})
            else:
                hangman.obj.stylized_echo('_ ', style={'fg':'yellow'}, echo={'nl': False})
        hangman.obj.echo('  ', nl=False)  # space between words

    hangman.obj.new_line()

    # output the clue, if provided
    if clue:
        hangman.obj.new_line()
        clue = clue.title()
        hangman.obj.stylized_echo('Clue: ', echo={'nl':False}, style={'fg':'yellow'})
        hangman.obj.echo_white(clue)
    hangman.obj.new_line()

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
        hangman.obj.stylized_echo(ch, echo={'nl':False}, style={'fg':color})
    hangman.obj.new_line()

def valid_choice(value):
    return len(value) == 1

@cli.command()
@pass_hangman
def ask_user(hangman):
    choice = None
    while not choice:
        choice = hangman.obj.styled_prompt("Pick any letter", style={'fg': "yellow"})
        choice = choice.lower()
        if choice == 'debug':
            # special operation to go into the debugger
            from IPython import embed;embed()
            choice = None
            continue
        if not valid_choice(choice):
            hangman.obj.styled_echo("Has to be just one character!", fg="red")
            choice = None
    return choice

@cli.command('setup_game')
@pass_hangman
def setup_game(hangman):
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

@cli.command()
@pass_hangman
def run(hangman):
    """
    Executes the main program loop
    """
    hangman.obj.clear_screen()   # blanks the screen
    hangman.invoke(setup_game)   # 
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
                say, what=hangman.obj.answer.split(' ')    # break up the answer into chunks of words with String.split()
            )
            hangman.obj.pause(info="")
            hangman.obj.clear_screen()
            over = True
            continue

        choice = hangman.invoke(ask_user)

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





