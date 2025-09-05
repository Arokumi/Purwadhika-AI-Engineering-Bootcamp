# curses_plotext_charts_colored.py
# Windows: pip install windows-curses plotext

import curses
import plotext as plt
import re

# -------------------------
# Demo data
# -------------------------
CARS = [
    (1, "BMW 320i (Luxury)"),
    (2, "Mercedes C200 (Luxury)"),
    (3, "Toyota Avanza (Family)"),
    (4, "Daihatsu Xenia (Family)"),
    (5, "Honda Brio (Budget)"),
    (6, "Toyota Agya (Budget)"),
]

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
REVENUE = [12.5, 13.1, 14.2, 16.0, 15.8, 17.4, 18.9, 19.2, 18.4, 20.1, 21.3, 22.0]

CATEGORY_LABELS = ["Luxury", "Family", "Budget"]
CATEGORY_REVENUE = [65, 25, 10]  # percentage share example

# -------------------------
# Strip ANSI from plotext (so curses doesn't show gibberish)
# -------------------------
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def clean(text: str) -> str:
    return ANSI_RE.sub("", text)


# -------------------------
# Plot builders (return list of lines)
# -------------------------
def build_line_plot(width: int, height: int):
    x_vals = list(range(len(MONTHS)))
    plt.clear_figure()
    plt.plotsize(width, height)
    plt.plot(x_vals, REVENUE, marker="dot")
    plt.xticks(x_vals, MONTHS)
    plt.xlim(-0.5, len(x_vals) - 0.5)
    plt.xlabel("Month")
    plt.ylabel("Revenue (Mio Rp)")
    plt.title("")
    return clean(plt.build()).splitlines()


def build_bar_plot(width: int, height: int):
    plt.clear_figure()
    plt.plotsize(width, height)
    plt.bar(MONTHS, REVENUE)
    plt.xlabel("Month")
    plt.ylabel("Revenue (Mio Rp)")
    plt.title("")
    return clean(plt.build()).splitlines()


def build_category_share_plot(width: int, height: int):
    """Pie substitute: vertical bar chart for category shares."""
    plt.clear_figure()
    plt.plotsize(width, height)
    plt.bar(CATEGORY_LABELS, CATEGORY_REVENUE)
    plt.ylabel("Revenue Share (%)")
    plt.title("")
    return clean(plt.build()).splitlines()


# -------------------------
# Screen drawing
# -------------------------
def draw_screen(stdscr, chart_type: str):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # layout split
    left_w = max(28, int(w * 0.45))
    right_w = max(20, w - left_w - 4)
    plot_h = max(8, h - 6)

    # Titles
    stdscr.addstr(0, 2, "Table of Cars", curses.A_BOLD)
    stdscr.hline(1, 1, curses.ACS_HLINE, max(1, left_w - 2))

    # Colored table
    y = 2
    for no, car in CARS:
        if y >= h - 3:
            break
        if "Luxury" in car:
            color = curses.color_pair(1)  # red
        elif "Family" in car:
            color = curses.color_pair(2)  # green
        else:
            color = curses.color_pair(4)  # blue

        line = f"{no:<3} | {car}"
        stdscr.addstr(y, 2, line[: max(0, left_w - 4)], color)
        y += 1

    # Choose plot
    if chart_type == "line":
        title = "Monthly Revenue (Line)"
        plot_lines = build_line_plot(right_w, plot_h)
    elif chart_type == "bar":
        title = "Monthly Revenue (Bar)"
        plot_lines = build_bar_plot(right_w, plot_h)
    elif chart_type == "category":
        title = "Revenue by Category (Bar)"
        plot_lines = build_category_share_plot(right_w, plot_h)
    else:
        title = "Unknown Chart"
        plot_lines = ["(invalid chart type)"]

    # Plot area
    stdscr.addstr(0, left_w + 2, title, curses.A_BOLD)
    stdscr.hline(1, left_w + 1, curses.ACS_HLINE, max(1, right_w))

    py = 2
    for line in plot_lines:
        if py >= h - 3:
            break
        stdscr.addstr(py, left_w + 2, line[:right_w])
        py += 1

    # Footer
    footer = "Press 1=line, 2=bar, 3=category; q=quit. Resize to redraw."
    stdscr.addstr(h - 2, 2, footer[: max(0, w - 4)])
    stdscr.refresh()


# -------------------------
# Main
# -------------------------
def main(stdscr):
    # Init curses
    curses.curs_set(0)
    stdscr.keypad(True)

    # Colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        # id=1..6 => foreground, default background
        curses.init_pair(1, curses.COLOR_RED, -1)  # Luxury
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Family
        curses.init_pair(4, curses.COLOR_BLUE, -1)  # Budget
    else:
        # still works without color
        pass

    chart_type = "line"
    draw_screen(stdscr, chart_type)

    while True:
        ch = stdscr.getch()
        if ch == ord("q"):
            break
        elif ch == ord("1"):
            chart_type = "line"
            draw_screen(stdscr, chart_type)
        elif ch == ord("2"):
            chart_type = "bar"
            draw_screen(stdscr, chart_type)
        elif ch == ord("3"):
            chart_type = "category"
            draw_screen(stdscr, chart_type)
        elif ch == curses.KEY_RESIZE:
            draw_screen(stdscr, chart_type)


if __name__ == "__main__":
    curses.wrapper(main)
