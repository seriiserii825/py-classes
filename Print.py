from rich import print


class Print:
    @staticmethod
    def print(message, error=False):
        if error:
            print("=" * 20)
            print(f"[red]{message}")
            print("=" * 20)
        else:
            print("=" * 20)
            print(f"[green]{message}")
            print("=" * 20)
