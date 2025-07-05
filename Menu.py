from rich import print

from MyTable import MyTable


class Menu:
    rows_count = 0

    @staticmethod
    def display():
        """
        Display the main menu options.
        """
        columns = [
            {"title": "Index", "style": "cyan"},
            {"title": "Option", "style": "white"},
        ]
        rows = [
            ["1", "Ruff format and check"],
            ["2", "Show contact form fields with required fields"],
            ["3", "Show contact form fields with submitted fields"],
            ["4", "Exit"],
        ]

        Menu.rows_count += len(rows)

        tb = MyTable()
        tb.show("Main Menu", columns, rows, row_styles={0: "magenta"})

    @staticmethod
    def choose_option():
        """
        Prompt the user to choose an option from the menu.
        """
        while True:
            try:
                count_range = f"Please enter a number between 1 and {Menu.rows_count}: "
                choice = int(input(count_range))
                if choice in range(1, Menu.rows_count + 1):
                    return choice
                else:
                    print(
                        f"[red]Invalid input."
                        f"Please enter a number between 1 and {Menu.rows_count}."
                    )
            except ValueError:
                print("[red] Input must be a number. Please try again.[/red]")
