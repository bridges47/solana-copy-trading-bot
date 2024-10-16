# To test or purchase the source code, contact @SolVolSupp_bot on Telegram
# To test or purchase the source code, contact @SolVolSupp_bot on Telegram
# To test or purchase the source code, contact @SolVolSupp_bot on Telegram

import curses
import requests
import json

# Main menu function
def main_menu(stdscr):
    curses.curs_set(0)  # Hide the cursor

    # Define the main menu items
    menu = {
        "main": [
            ("💊COPY-TRADING", "COPY"),
            ("💎 Volume Bot", "volume"),
            ("🎯 Snipe Bot", "army"),
            ("🤖 Bump Bot", "bump"),
            ("💲 Create Token Bundler", "token"),
            ("⚠️ Wallet Set", "wallet"),
            ("📊 Liquidity Management", "liquidity_management"),
            ("🔄 Market-Making & Trading Bots", "market_making"),
            ("📦 Batch Operations", "batch_operations"),
            ("⚙️ Settings", "settings"),
            ("💰 Pump Strategies", "pump_strategies"),
            ("📜 Convenient Tools", "convenient_tools"),
            ("❌ Exit", "exit")
        ]
    }

    # ASCII title art for decoration
    title = [
r" /      \ /      \|  \     |  \   |  \/      \|  \     |  \  |  \  \     /  \        \ ",
r"|  ▓▓▓▓▓▓\  ▓▓▓▓▓▓\ ▓▓     | ▓▓   | ▓▓  ▓▓▓▓▓▓\ ▓▓     | ▓▓  | ▓▓ ▓▓\   /  ▓▓ ▓▓▓▓▓▓▓▓ ",
r"| ▓▓___\▓▓ ▓▓  | ▓▓ ▓▓     | ▓▓   | ▓▓ ▓▓  | ▓▓ ▓▓     | ▓▓  | ▓▓ ▓▓▓\ /  ▓▓▓ ▓▓__     ",
r" \▓▓    \| ▓▓  | ▓▓ ▓▓      \▓▓\ /  ▓▓ ▓▓  | ▓▓ ▓▓     | ▓▓  | ▓▓ ▓▓▓▓\  ▓▓▓▓ ▓▓  \    ",
r" _\▓▓▓▓▓▓\ ▓▓  | ▓▓ ▓▓       \▓▓\  ▓▓| ▓▓  | ▓▓ ▓▓     | ▓▓  | ▓▓ ▓▓\▓▓ ▓▓ ▓▓ ▓▓▓▓▓    ",
r"|  \__| ▓▓ ▓▓__/ ▓▓ ▓▓_____   \▓▓ ▓▓ | ▓▓__/ ▓▓ ▓▓_____| ▓▓__/ ▓▓ ▓▓ \▓▓▓| ▓▓ ▓▓_____ ",
r" \▓▓    ▓▓\▓▓    ▓▓ ▓▓     \   \▓▓▓   \▓▓    ▓▓ ▓▓     \\ ▓▓    ▓▓ ▓▓  \▓ | ▓▓ ▓▓     \ ",
r"  \▓▓▓▓▓▓  \▓▓▓▓▓▓ \▓▓▓▓▓▓▓▓    \▓     \▓▓▓▓▓▓ \▓▓▓▓▓▓▓▓ \▓▓▓▓▓▓ \▓▓      \▓▓\▓▓▓▓▓▓▓▓ "
    ]

    def print_menu(stdscr, selected_row_idx):
        """Prints the menu and highlights the selected item."""
        stdscr.clear()

        # Print the title
        for i, line in enumerate(title):
            stdscr.addstr(i, 0, line, curses.color_pair(4))
        stdscr.addstr(len(title) + 1, 0, "Original Dev: @SolVolSupp_bot on Telegram", curses.color_pair(3))
        stdscr.addstr(len(title) + 2, 0, "Main Menu", curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(len(title) + 3, 0, "Use arrow-keys. Return to submit.", curses.color_pair(3))

        # Print the menu items
        current_menu_items = menu["main"]
        for idx, item in enumerate(current_menu_items):
            x = 0
            y = idx + len(title) + 5
            if idx == selected_row_idx:
                stdscr.addstr(y, x, item[0], curses.color_pair(1))  # Highlight the selected item
            else:
                stdscr.addstr(y, x, item[0])
        stdscr.refresh()

    # Initialize color pairs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted menu item
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Title color
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Subtitle color
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Bright green title color

    current_row = 0  # Start with the first item selected
    print_menu(stdscr, current_row)

    # Main loop to handle user input
    while True:
        key = stdscr.getch()

        # Handle up and down arrow keys to navigate the menu
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu["main"]) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_item = menu["main"][current_row][1]

            # Exit the program
            if selected_item == "exit":
                break
            # Connect to RPC and display the result
            elif selected_item == "connect_rpc":
                rpc_result = connect_to_rpc()
                stdscr.addstr(len(title) + len(menu["main"]) + 6, 0, f"RPC Result: {rpc_result}", curses.color_pair(3))
            # Fetch data from PUMP.FUN and display it
            elif selected_item == "pump_fun_data":
                pump_data = get_pump_fun_data()
                stdscr.addstr(len(title) + len(menu["main"]) + 6, 0, f"PUMP.FUN Data: {pump_data}", curses.color_pair(3))
            else:
                # Handle other menu options (placeholder for future functionalities)
                stdscr.addstr(len(title) + len(menu["main"]) + 6, 0, f"You selected {menu['main'][current_row][0]}!", curses.color_pair(3))

            stdscr.refresh()
            stdscr.getch()  # Wait for user to press a key before refreshing the menu

        # Refresh the menu display
        print_menu(stdscr, current_row)

if __name__ == "__main__":
    curses.wrapper(main_menu)

# To test or purchase the source code, contact @SolVolSupp_bot on Telegram