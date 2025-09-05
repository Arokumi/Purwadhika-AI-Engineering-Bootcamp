import curses

MENU = ["List Cars", "Rent a Car", "My Rentals", "Statistics", "Quit"]


def draw_menu(stdscr, idx):
    stdscr.clear()
    stdscr.addstr(0, 2, "Car Rental — Admin", curses.A_BOLD)
    for i, item in enumerate(MENU, start=2):
        attr = curses.A_REVERSE if (i - 2) == idx else curses.A_NORMAL
        stdscr.addstr(i, 4, item, attr)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    idx = 0
    while True:
        draw_menu(stdscr, idx)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(MENU)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(MENU)
        elif key in (curses.KEY_ENTER, 10, 13):
            choice = MENU[idx]
            if choice == "Quit":
                break
            # call your core functions here, then show a sub-screen
            # e.g., show_list_cars(stdscr) that renders a table
        elif key == 27:  # ESC
            break


if __name__ == "__main__":
    curses.wrapper(main)
