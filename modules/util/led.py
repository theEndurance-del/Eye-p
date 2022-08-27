"""
A line based text editor for note taking purposes.

It is a very basic and minimal text editor working on line based editing.
"""

import os
import readline
from modules.util.extra import get_args, completer, completers

completer = completer(completers.led)


class start_editor:
    def __init__(self, argslist: list):
        """Initiate the editor with the arguments"""

        self.argslist = argslist

    def args(self, pos=None):
        """
        Retrieve arguments from the interpreter.

        This function is not related to utils.args in any sense.
        """
        if pos:
            return self.argslist[pos]
        else:
            return self.argslist

    def start_led(self):
        """Call the driver function for the editor"""
        self.led()

    def write(self, file_name, final_buffer):
        """write the buffer to given file"""
        final_buffer_string = "\n".join(final_buffer)
        write_file = open(file_name, "w")
        write_file.write(final_buffer_string + "\n")
        write_file.close()

    def read_file(self):
        """
        Read from the given file if any
        - The path to file should not be a relative path but an absolute one
        """
        try:
            file_path: str = self.args(1)
            if file_path:
                if os.path.exists(file_path):
                    fr = open(file_path, "r")
                    file_content_string = fr.read()
                    fr.close()
                    file_content = file_content_string.split("\n")
                    file_content.pop(len(file_content) - 1)
                    return file_content
                else:
                    return []
        except IndexError:
            return []

    def change(self, pos, original_buffer):
        """
        Function to change a specific replace

        Not to be confised with search and replace(it is yet to be implemented)
        """
        temp_buffer = []
        while True:
            c = input()
            if c != "~|":
                temp_buffer.append(c)
            else:
                break

        temp_buffer_string = "\n".join(temp_buffer)
        original_buffer[pos] = temp_buffer_string
        original_buffer_string = "\n".join(original_buffer)
        return original_buffer_string.split("\n")

    def led(self):
        """Start the interpreter for the interpreter."""

        try:
            mode: str = "normal"
            led_buffer: list = self.read_file()
            pos: int = 0

            while True:
                if mode == "normal":
                    readline.parse_and_bind("tab: complete")
                    readline.set_completer(completer.completion)
                    c = input(f"{mode}> ")
                else:
                    readline.parse_and_bind("tab: nocomplete")
                    c = input()

                cmd = c.split()
                if mode == "normal":
                    if c in [None, ""]:
                        pass

                    elif get_args(cmd, 0) in ["insert", "i"]:
                        mode = "insert"

                    elif get_args(cmd, 0) in ["change", "c"]:
                        if get_args(cmd, 1) and led_buffer[int(get_args(cmd, 1)) - 1]:
                            led_buffer = self.change(
                                int(get_args(cmd, 1)) - 1, led_buffer
                            )
                        else:
                            print("Error")

                    elif get_args(cmd, 0) in ["print", "p"]:
                        for x in led_buffer:
                            print(x)

                    elif get_args(cmd, 0) in ["lineprint", "n"]:
                        for ln, text in enumerate(led_buffer):
                            print(f"{ln+1}\t | {text}")

                    elif get_args(cmd, 0) in ["write", "w"]:
                        if get_args(cmd, 1):
                            self.write(get_args(cmd, 1), led_buffer)
                        elif self.args(1):
                            self.write(self.args(1), led_buffer)
                        else:
                            print("Err: Invalid Filename")

                    elif get_args(cmd, 0) in ["quit", "q"]:
                        break

                    else:
                        print(f"Err: Invalid instruction: {get_args(cmd, 0)}")

                elif mode == "insert":
                    if c != "~|":
                        led_buffer.append(c)
                        pos += 1

                    else:
                        mode = "normal"
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
