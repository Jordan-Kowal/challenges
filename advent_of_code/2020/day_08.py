"""Day 8 challenge"""

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Program:
    def __init__(self, instructions):
        """
        Creates a program made of a list of ordered instructions
        :param [Instruction] instructions: The instructions the program will run
        """
        self.instructions = instructions
        self.reset()

    def run(self):
        """Runs the program and stops when it detects the infinite loop"""
        self.reset()
        while self.index < len(self.instructions):
            instruction = self.instructions[self.index]
            if instruction.times >= 1:
                self.stuck = True
                break
            instruction.exec(self)

    def run_with_fix(self):
        """
        Runs the program N times by trying to fix ONE 'nop' or 'jmp' instructions
        Loops over the available instructions until it finds the right one
        """
        for i, instruction in enumerate(self.instructions):
            # ACC are not corrupted
            if instruction.name == "acc":
                continue
            # NOP fix might crash the system
            if instruction.name == "nop":
                is_infinite_loop = instruction.value == 0
                negative_index = instruction.value <= 0 and instruction.value < -i
                index_too_big = instruction.value > 0 and instruction.value + i >= len(
                    self.instructions
                )
                if is_infinite_loop or negative_index or index_too_big:
                    continue
            previous_name = instruction.name
            instruction.name = "nop" if instruction.name == "jmp" else "jmp"
            self.run()
            if not self.stuck:
                break
            instruction.name = previous_name
            self.reset()

    def reset(self):
        """Simply resets the program and its instructions to its default/starting state"""
        for instruction in self.instructions:
            instruction.times = 0
        self.acc = 0
        self.stuck = False
        self.index = 0


class Instruction:
    def __init__(self, line):
        """
        Creates a callable instruction from the input line
        :param str line: The input line to parse to get the instruction
        """
        name, value = line.split(" ")
        self.line = line
        self.name = name
        self.value = int(value)
        self.times = 0

    def __str__(self):
        """
        :return: The initial input line
        :rtype: str
        """
        return self.line

    def exec(self, program):
        """
        Runs the instruction for a given program
        The function to call is based on the instruction's name
        :param Program program: The program calling this instruction
        """
        self.times += 1
        function_to_run = getattr(self, self.name)
        function_to_run(program)

    def acc(self, program):
        """
        Increments the program's accumulator by the value, and index by 1
        :param Program program: The program calling this instruction
        """
        program.acc += self.value
        program.index += 1

    def jmp(self, program):
        """
        Changes the program's index by the instruction value
        :param Program program: The program calling this instruction
        """
        program.index += self.value

    @staticmethod
    def nop(program):
        """
        Simply moves to the next instruction by increasing the program's index by 1
        :param Program program: The program calling this instruction
        """
        program.index += 1


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
instructions = [Instruction(line) for line in read_input("day_08.txt")]
main_program = Program(instructions)

# Problem 1
main_program.run()
print(main_program.acc)

# Problem 2
main_program.run_with_fix()
print(main_program.acc)
