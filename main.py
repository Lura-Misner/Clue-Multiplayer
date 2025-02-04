import constants
import pygame
import sys
from client import Client
from _thread import *
from tkinter import *


def notes_set_up():
    """
    Code used from https://www.geeksforgeeks.org/build-a-basic-text-editor-using-tkinter-in-python/
    Allows there to be a basic text editor available where the player can keep customized notes throughout the game
    """
    root = Tk()
    root.geometry("500x500")
    root.title("Clue Notes - Don't Close")
    root.minsize(height=400, width=400)
    root.maxsize(height=400, width=400)

    # adding scrollbar
    scrollbar = Scrollbar(root)

    # packing scrollbar
    scrollbar.pack(side=RIGHT,
                   fill=Y)

    text_info = Text(root,
                     yscrollcommand=scrollbar.set)
    text_info.pack(fill=BOTH)

    # configuring the scrollbar
    scrollbar.config(command=text_info.yview)

    root.mainloop()


def main():
    # Pygame initializations
    pygame.init()
    WIN = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption("Clue")
    clock = pygame.time.Clock()

    # Make a client object
    client = Client(WIN)

    # Make sure that the choice selected by the user is valid
    print("Selecting character...")
    try:
        client.select_character()
    except TypeError:
        print("Please start the server")
        sys.exit()

    # How to wait for the start
    #client.wait_for_start()

    #ready = False
    #while not ready:
        #client.show_ready()
        #pygame.display.update()
        #ready = client.n.send('start')

    print("Starting game...")

    # Some flags to keep track of if the game is quit early, if the player gets disqualified, and turn number
    disqualified = False
    run = True

    while run:
        client.draw_screen()

        # Handle our turn
        if client.check_our_turn():
            if not disqualified:
                client.handle_turn()
                client.draw_screen()

        # If it's not our turn, check for a suggestion
        if not client.check_our_turn():
            pending_suggestion = client.check_pending_suggestion()
            waiting_on = client.waiting_on_you()

            # If there is a pending suggestion, display it to the user
            if pending_suggestion:

                # Get the suggestion to display it to the user
                suggestion_text = client.ask_server('get_last_suggestion')
                full = f'{suggestion_text.get_character()} with the {suggestion_text.get_weapon()}' \
                       f' in the {suggestion_text.get_room()}'

                client.draw_text(f'{suggestion_text.get_player()} has made a suggestion', 24, constants.SCARLET,
                                 650, 475)

                if len(full) <= 60:
                    client.draw_text(full, 18, constants.SCARLET, 640, 500)
                else:
                    client.draw_text(full, 18, constants.SCARLET, 620, 500)

            # If there is a pending suggestion and its waiting on you, respond to it
            if pending_suggestion is True and waiting_on is True:
                print("You have a suggestion to respond to...")
                client.respond_suggestion()

        # Check if our player is disqualified from the match
        if not disqualified:
            disqualified = client.ask_server('check_disqualified')

        # If the player has been disqualified, then add information to the screen to inform them
        if disqualified:
            client.draw_disqualification()

        # If the game has been won, then display the wining screen
        game_finished = client.ask_server('game_finished')
        if game_finished:
            run = False
            client.draw_end_screen()

        # If the game is quit early, then let the server that this player has quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Send a signal to the server that the game is being quit early
                client.ask_server('quit')
                run = False

        # Update the window
        pygame.display.update()
        clock.tick(60)


start_new_thread(notes_set_up, ())
main()
