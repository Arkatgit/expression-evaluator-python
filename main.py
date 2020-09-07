import logging
from parser import Parser


def repl(prompt: str = "Expr-> ") -> str:
    while True:
        expr_str = input(prompt)
        if expr_str == "quit":
            return
        parser = Parser(expr_str)
        print("Ans:-> {}".format(parser.parse()))


def main():
    logging.basicConfig(level=logging.ERROR)
    repl()

main()
    
