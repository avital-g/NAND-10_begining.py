"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

STATIC ="static"
LOCAL = "local"
ARGUMENT = "argument"
THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"
CONSTANT = "constant"

PUSH = "push"
POP = "pop"




arthmatic_dict = {"=": "EQ",">": "GT", "<": "LT","&" :"AND", "|": "OR","~": "NOT", "<<": "SHIFTLEFT", ">>" : "SHIFTRIGHT"}

class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output_stream =output_stream
        self.file_name = output_stream.name

    def write_to_file(self, to_write):
        print(to_write + "\n")
        self.output_stream.write(to_write + "\n")

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        self.write_to_file(PUSH+" "+segment +" "+str(index))

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        self.write_to_file(POP+" "+segment +" "+str(index))


    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self.write_to_file(arthmatic_dict[command])

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.write_to_file("@"+label)

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.write_to_file("goto "+label)

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.write_to_file("if-goto "+label)

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.write_to_file("call "+name+ " "+str(n_args))

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.write_to_file("function "+self.file_name+"."+name+ str(n_locals))

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.write_to_file("return")
