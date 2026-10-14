
import os
import sys


class ApprovalManager:
    # Shared confirmation input for all write operations
    def request_approval(self, question: str) -> bool:
        print(f"{question} [y/N]: ", end="", flush=True)
        buffer = []

        while True:
            char = self.get_char()

            if char == "\x1b":  # Escape
                print()
                return False

            if char in ("\r", "\n"):
                answer = "".join(buffer).strip().lower()
                print()

                if answer in ("yes", "y"):
                    return True
                if answer in ("", "no", "n"):
                    return False

                print("Type yes to approve or no to cancel: ", end="", flush=True)
                buffer.clear()

            elif char in ("\x08", "\x7f"):  # Backspace
                if buffer:
                    buffer.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            elif char.isprintable():
                buffer.append(char)
                sys.stdout.write(char)
                sys.stdout.flush()

    def text_replacement(
        self,
        path: str,
        old_text: str,
        new_text: str
    ) -> bool:
        print(f"\nZayn wants to edit: {path}")
        print("Old text:")
        print(old_text)
        print("New text:")
        print(new_text if new_text else "(remove old text)")

        return self.request_approval("Apply this change?")

    def file_creation(
        self,
        path: str,
        content: str,
        encoding: str,
        data: bytes
    ) -> bool:
        print(f"\nZayn wants to create: {path}")
        print(f"Encoding: {encoding}, size: {len(data)} bytes")

        if encoding == "utf-8":
            print("Content:")
            print(content if content else "(empty file)")
        else:
            print("Content: (binary data, not displayed)")

        return self.request_approval("Create file?")

    #get key input
    def get_char(self) -> str:
        if os.name == 'nt':  # Windows
            import msvcrt
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):  # Special key prefix (e.g., arrow keys)
                msvcrt.getch()
                return ''
            return ch.decode('utf-8', errors='ignore')
        else:  # Unix / Linux / macOS
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def file_deletion(self, path: str, size: int) -> bool:
        print(f"\nZayn wants to delete: {path}")
        print(f"Size: {size} bytes")
        print("This permanently deletes the file. It does not use the recycle bin.")

        return self.request_approval("Delete this file?")
