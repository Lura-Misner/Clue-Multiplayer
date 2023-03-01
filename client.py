import time
import constants
import pygame
import random
from board import Board
from characters import Characters
from network import Network
from roomtype import RoomType


WIN = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("Clue")
pygame.init()
card_map = {}


def draw_screen(board, cards, character, notes, player_positions, current_turn):
    board.draw_board()
    draw_players(player_positions, board)
    draw_cards(cards)
    draw_notes(character.value, notes)
    draw_turn(current_turn)


def draw_players(player_positions, board):
    for character, position in player_positions.items():
        square = board.get_mapping(position)
        x, y = square[0], square[1]
        x_length, y_length = square[2], square[3]

        center_x = x + (x_length // 2)
        center_y = y + (y_length // 2)

        pygame.draw.circle(WIN, constants.BLACK, (center_x, center_y), (x_length // 2.5) + 3)
        font = pygame.font.SysFont('freesansbold.ttf', 18)

        if character == Characters.COLONEL_MUSTARD.value:
            pygame.draw.circle(WIN, constants.MUSTARD, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('M', True, constants.BLACK), (center_x - 5, center_y - 5))
        elif character == Characters.MRS_WHITE.value:
            pygame.draw.circle(WIN, constants.WHITE, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('W', True, constants.BLACK), (center_x - 5, center_y - 5))
        elif character == Characters.MR_PEACOCK.value:
            pygame.draw.circle(WIN, constants.PEACOCK, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('PK', True, constants.BLACK), (center_x - 8, center_y - 5))
        elif character == Characters.MISS_SCARLET.value:
            pygame.draw.circle(WIN, constants.SCARLET, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('S', True, constants.BLACK), (center_x - 4, center_y - 5))
        elif character == Characters.PROFESSOR_PLUM.value:
            pygame.draw.circle(WIN, constants.PLUM, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('PL', True, constants.BLACK), (center_x - 8, center_y - 5))
        else:
            pygame.draw.circle(WIN, constants.GREEN, (center_x, center_y), x_length // 2.5)
            WIN.blit(font.render('G', True, constants.BLACK), (center_x - 5, center_y - 5))


def draw_turn(who):
    font = pygame.font.SysFont('freesansbold.ttf', 24)
    WIN.blit(font.render(f"It's {who.get_character().value}'s turn", True, constants.BLACK), (700, 725))


def draw_moves(move):
    font = pygame.font.SysFont('freesansbold.ttf', 24)
    WIN.blit(font.render(f'You have {move} moves left', True, constants.SCARLET), (700, 700))


def draw_notes(name, notes):
    header = pygame.font.SysFont('freesansbold.ttf', 32)
    title = pygame.font.SysFont('freesansbold.ttf', 24)
    font = pygame.font.SysFont('freesansbold.ttf', 20)

    WIN.blit(header.render(f"{name}'s notes", True, constants.BLACK), (675, 30))

    # Characters
    WIN.blit(title.render("It can't be these characters: ", True, constants.BLACK), (675, 70))
    for i, character in enumerate(notes[0]):
        x = 680 + (i//4 * 125)
        y = 95 + ((i % 4) * 20)
        WIN.blit(font.render(f"{character}", True, constants.BLACK), (x, y))

    # Weapons
    WIN.blit(title.render("It can't be these weapons: ", True, constants.BLACK), (675, 200))
    for i, weapon in enumerate(notes[1]):
        x = 680 + (i//4 * 125)
        y = 225 + ((i % 4) * 20)
        WIN.blit(font.render(f"{weapon}", True, constants.BLACK), (x, y))

    # Locations
    WIN.blit(title.render("It can't be these locations: ", True, constants.BLACK), (675, 325))
    for i, location in enumerate(notes[2]):
        x = 680 + (i//4 * 125)
        y = 350 + ((i % 4) * 20)
        WIN.blit(font.render(f"{location}", True, constants.BLACK), (x, y))


def draw_cards(cards):
    title = pygame.font.SysFont('freesansbold.ttf', 20)
    font = pygame.font.SysFont('freesansbold.ttf', 14)
    WIN.blit(title.render('Your cards ', True, constants.BLACK), (265, 635))

    for i, card in enumerate(cards):
        x = 10 + ((i % 6) * 100)
        y = 655 + (30 * (i // 6))

        rect = pygame.Rect(x, y, constants.CARD_SIZE_X, constants.CARD_SIZE_Y)
        pygame.draw.rect(WIN, constants.CARD, rect)
        card_value = card.get_value()
        card_map[card_value] = (x, y)

        WIN.blit(font.render(f'{card_value}', True, constants.BLACK),
                 (x + 2.5*(17 - len(card_value)), y + 5))


def show_ready(n):
    # Show how many players are ready
    WIN.fill(constants.BACKGROUND)
    num_ready = n.send('num_ready')
    font = pygame.font.SysFont('freesansbold.ttf', 56)
    WIN.blit(font.render(f'Waiting on other players...', True, (0, 0, 0)), (275, 200))
    WIN.blit(font.render(f'{num_ready[1]} out of {num_ready[0]} players ready', True, constants.BLACK), (275, 275))


def select_character(n) -> Characters:
    selection_made = False
    choice = None

    while not selection_made:
        available_characters = n.send('character_selection')
        WIN.fill(constants.BACKGROUND)

        # How many players ready
        num_ready = n.send('num_ready')
        font1 = pygame.font.SysFont('freesansbold.ttf', 26)
        WIN.blit(font1.render(f'{num_ready[1]} out of {num_ready[0]} players ready', True, constants.BLACK), (50, 50))

        # Title
        header = pygame.font.SysFont('freesansbold.ttf', 60)
        font = pygame.font.SysFont('freesansbold.ttf', 32)

        WIN.blit(header.render('Select a Character', True, constants.BLACK), (300, 200))

        mapping = {}
        # Character options
        for i, ch in enumerate(available_characters):
            x = 75 + i * 150
            y = 300
            mapping[ch] = (x, y)

            if ch == Characters.COLONEL_MUSTARD:
                color = constants.MUSTARD
            elif ch == Characters.MISS_SCARLET:
                color = constants.SCARLET
            elif ch == Characters.MR_PEACOCK:
                color = constants.PEACOCK
            elif ch == Characters.MRS_WHITE:
                color = constants.WHITE
            elif ch == Characters.PROFESSOR_PLUM:
                color = constants.PLUM
            else:
                # Reverend Green
                color = constants.GREEN

            rect = pygame.Rect(x, y, constants.CHARACTER_SELECTION_SIZE, constants.CHARACTER_SELECTION_SIZE)
            pygame.draw.rect(WIN, color, rect)

        # Listen for clicks
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

                # Find out if the click maps to a character
                for key in mapping.keys():
                    x, y = pos
                    x2, y2 = mapping[key]

                    if x2 < x < x2 + constants.CHARACTER_SELECTION_SIZE and \
                            y2 < y < y2 + constants.CHARACTER_SELECTION_SIZE:
                        choice = key

                # Check if it is the confirmation button
                if choice:
                    # Clicking confirmed
                    x, y = pos
                    if 425 <= x <= 425 + 125 and 600 <= y <= 600 + 65:
                        selection_made = True

        # Selection update
        WIN.blit(font.render('Character Selected: ', True, constants.BLACK), (300, 500))

        if choice:
            # If a choice has been made, add a confirmation button to create the player
            WIN.blit(font.render(choice.value, True, constants.BLACK), (550, 500))

            # Button to confirm selection (will confirm the selection made if choice != None
            rect = pygame.Rect(425, 600, 125, 65)
            pygame.draw.rect(WIN, (0, 0, 0), rect)
            rect = pygame.Rect(427, 602, 121, 61)
            pygame.draw.rect(WIN, (0, 255, 0), rect)

            WIN.blit(font.render('Confirm', True, constants.BLACK), (442, 622))

        pygame.display.update()

    return choice


def is_entrance(board, space) -> bool:
    for key in board.entrances.keys():
        if space in board.entrances[key]:
            return True

    return False


def calculate_valid_moves(board, character, player_positions) -> [str]:
    directions = []
    position = player_positions[character.value]

    # This chunk adds the option for the user to use secret passages when in particular rooms
    # But also to allow the user to pick an entrance to leave from (if there are multiple)
    if position in board.entrances['Kitchen']:
        directions.append('Kitchen')
    elif position in board.entrances['Study']:
        directions.append('Kitchen')
    elif position in board.entrances['Lounge']:
        directions.append('Conservatory')
    elif position in board.entrances['Conservatory']:
        directions.append('Lounge')

    # TODO: some places have multiple entrances, so when it comes to leaving the room, then they will have
    # TODO: to pick an exit

    def occupied(space) -> bool:
        for key in player_positions.keys():
            if space == player_positions[key]:
                return True

        return False

    # Check for valid movements (right, left, down, up).
    dr = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    row = position // 24
    col = position % 24
    ind = 0
    for r, c in dr:
        nr = row + r
        nc = col + c
        space_id = (nr * 24) + nc

        # Verify that the rows and columns are within the proper ranges
        if 0 <= nr < 25 and 0 <= nc < 24:
            if (not occupied(space_id) and board.board[space_id].get_room()) == RoomType.HALLWAY \
               or is_entrance(board, space_id):
                # Add the position to the valid directions dictionary
                if ind == 0:
                    directions.append('Right')
                elif ind == 1:
                    directions.append('Left')
                elif ind == 2:
                    directions.append('Down')
                else:
                    directions.append('Up')
        ind += 1

    return directions


def give_room_position(board, player_position) -> int:
    room = None
    for r in board.entrances.keys():
        if player_position in board.entrances[r]:
            room = r

    for i in range(6):
        if board.room_occupied[room][i]:
            continue
        else:
            board.room_occupied[room][i] = True
            return board.room_display[room][i]

    # Shouldn't ever get here
    print("Error: Room full")
    return -1


def free_position(board, room, position):
    if room in board.room_occupied:
        if position in board.room_display[room]:
            index = board.room_display[room].index(position)
            board.room_occupied[room][index] = False


def pick_exit(board, room):
    font = pygame.font.SysFont('freesansbold.ttf', 24)
    WIN.blit(font.render(f'Select an exit from {room} by clicking on it', True, constants.SCARLET), (650, 700))

    while True:
        # Listen for clicks
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONUP:
                x2, y2 = pygame.mouse.get_pos()

                if room in board.entrances:
                    for entrance in board.entrances[room]:
                        x, y, x_length, y_length = board.get_mapping(entrance)

                        if x <= x2 <= x + x_length and y <= y2 <= y + y_length:
                            return entrance
        pygame.display.update()


def handle_turn(board, cards, character, notes, player_positions, current_turn) -> {str: int}:

    # If they are in a room, then let them pick an exit of that room to use
    room = board.in_room(player_positions[character.value])
    exiting = False
    if room not in ['Hallway', 'OFB', 'Start']:
        # Free the position in the room
        free_position(board, room, player_positions[character.value])

        if len(board.entrances[room]) > 1:
            player_positions[character.value] = pick_exit(board, room)
        else:
            player_positions[character.value] = board.entrances[room][0]

        exiting = True

    moves = random.randint(2, 12)
    pygame.event.clear()

    while moves > 0:
        valid_moves = calculate_valid_moves(board, character, player_positions)
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if 'Right' in valid_moves:
                        player_positions[character.value] += 1
                        moves -= 1
                        exiting = False

                elif event.key == pygame.K_LEFT:
                    if 'Left' in valid_moves:
                        player_positions[character.value] -= 1
                        moves -= 1
                        exiting = False

                elif event.key == pygame.K_DOWN:
                    if 'Down' in valid_moves:
                        player_positions[character.value] += 24
                        moves -= 1
                        exiting = False

                elif event.key == pygame.K_UP:
                    if 'Up' in valid_moves:
                        player_positions[character.value] -= 24
                        moves -= 1
                        exiting = False

        # Handle a player entering the room
        if not exiting and is_entrance(board, player_positions[character.value]):
            moves = 0
            player_positions[character.value] = give_room_position(board, player_positions[character.value])

        draw_screen(board, cards, character, notes, player_positions, current_turn)
        draw_moves(moves)
        pygame.display.update()
    return player_positions


def main():
    n = Network()
    print("Selecting character...")
    selected = select_character(n)
    print("Creating player...")
    n.send(selected.value)

    # How to wait for the start
    ready = False
    while not ready:
        show_ready(n)
        pygame.display.update()
        ready = n.send('start')

    print("Starting game...")
    board = Board(WIN)

    print("Getting cards...")
    cards = n.send(f'get_cards {selected.value}')

    print("Getting notes...")
    notes = n.send(f'get_notes {selected.value}')

    game_finished = False
    previous_turn = 0
    current_turn = n.send('whos_turn')
    player_positions = n.send('get_all_positions')

    while not game_finished:
        # Ask whose turn it is
        turn_num = n.send('turn')

        # If a player has moved, then get the positions of all players
        if turn_num != previous_turn:
            current_turn = n.send('whos_turn')
            previous_turn = current_turn
            player_positions = n.send('get_all_positions')

        # Draw the board
        draw_screen(board, cards, selected, notes, player_positions, current_turn)

        # Handle our turn
        if current_turn.get_character().value == selected.value:
            player_positions = handle_turn(board, cards, selected, notes, player_positions, current_turn)
            n.send(f'update_position {selected.value},{player_positions[selected.value]}')
            n.send('turn_done')

        pygame.display.update()
        game_finished = n.send('game_finished')
        time.sleep(2)


main()
