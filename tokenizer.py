from dataclasses import dataclass
from enum import Enum

def repl(prompt: str = "Expr-> ") -> str:
    while True:
        expr_str = input(prompt)
        print(expr_str)
        if input == "quit":
            return

class Token(Enum):
    TOKERR    = -1
    TOKEOLN   =  0
    TOKPLUS   =  2
    TOKMINUS  =  3
    TOKMUL    =  4
    TOKDIVIDE =  5
    TOKMOD    =  6
    TOKIDENT  =  7
    TOKNUMBER =  8
    TOKCOMMA  =  9
    TOKLPAREN =  10
    TOKRPAREN =  11
    TOKEQUAL  =  12

@dataclass
class TokenInfo:
    token: Token
    lexeme: str
    col_no: int

class Tokenizer:
    def __init__(self, expr_str: str):
        self.expr_str = expr_str
        self.current_pos = -1
        self.length_of_expr_str = len(expr_str)

    def get_next_token(self) -> TokenInfo:
        tok = None
        while tok == None:
            self.current_pos += 1
            if  self.current_pos >= len(self.expr_str) or self.expr_str[self.current_pos] == '\n':
                tok = TokenInfo(Token.TOKEOLN, '\n', self.current_pos)
            #skip whitespaces
            elif self.expr_str[self.current_pos].isspace():
                continue

            elif  self.current_pos == len(self.expr_str) - 1:  # Also cater for non newline terminated strs
                tok = TokenInfo(Token.TOKEOLN, '\n', self.current_pos)

            elif  self.expr_str[self.current_pos] == '+':
                tok = TokenInfo(Token.TOKPLUS, '+', self.current_pos)

            elif  self.expr_str[self.current_pos] == '-':
                tok = TokenInfo(Token.TOKMINUS, '-', self.current_pos)

            elif  self.expr_str[self.current_pos] == '*':
                tok = TokenInfo(Token.TOKMUL, '*', self.current_pos)

            elif  self.expr_str[self.current_pos] == '/':
                tok = TokenInfo(Token.TOKDIVIDE, '/', self.current_pos)

            elif  self.expr_str[self.current_pos] == '%':
                tok = TokenInfo(Token.TOKMOD, '%', self.current_pos)

            elif  self.expr_str[self.current_pos] == '(':
                tok = TokenInfo(Token.TOKLPAREN, '(', self.current_pos)

            elif  self.expr_str[self.current_pos] == ')':
                tok = TokenInfo(Token.TOKRPAREN, ')', self.current_pos)

            elif  self.expr_str[self.current_pos] == ',':
                tok = TokenInfo(Token.TOKCOMMA, ',', self.current_pos)

            elif  self.expr_str[self.current_pos] == '=':
                tok = TokenInfo(Token.TOKEQUAL, '=', self.current_pos)

            elif  self.expr_str[self.current_pos].isalpha():
                tok = self._scan_identifier()

            elif  self.expr_str[self.current_pos].isdigit():
                tok = self._scan_number()

            else:
                print("Error:Column {}: Unrecognized character '{}' found in input".format(self.current_pos + 1, self.expr_str[self.current_pos]))
                self.current_pos += 1

        return tok

    def _scan_identifier(self) -> TokenInfo:
        """
            Finite state machine to recognize an identifier
            Using the regex ->  "a" - "z" {"a" - "z" "0" - "9" "_"}
        """
        state = 0    #start state
        lexeme = ""
        col_no = self.current_pos

        while True:
            if state == 0:
                if self.expr_str[self.current_pos].isalpha(): #this check can actually be ignored since we already know the first is a char
                    state = 1
                    lexeme += self.expr_str[self.current_pos]

            elif state == 1:
                if self._is_index_within_range() and (self.expr_str[self.current_pos].isalnum() or self.expr_str[self.current_pos] == '_'):
                    state = 1
                    lexeme += self.expr_str[self.current_pos]
                else:
                    state = 2

            elif state == 2:  #accept state
                #backtrack and accept
                self.current_pos -= 1
                return TokenInfo(Token.TOKIDENT, lexeme, col_no)

            self.current_pos += 1

    def _scan_number(self) -> TokenInfo:
        """
            Finite state machine to recognize an number
            Using the production

        """
        state = 0
        lexeme = ""
        col_no = self.current_pos

        while True:
            if state == 0:
                if self.expr_str[self.current_pos].isdigit():
                    state = 1
                    lexeme += self.expr_str[self.current_pos]

            elif state == 1:
                if self._is_index_within_range and self.expr_str[self.current_pos].isdigit():
                    state = 1
                    lexeme += self.expr_str[self.current_pos]

                elif self._is_index_within_range and self.expr_str[self.current_pos] == '.':
                    state = 2
                    lexeme += self.expr_str[self.current_pos]

                else: #accepting
                    # we implicity assume it state 3 and accept just to save code
                    self.current_pos -= 1
                    return TokenInfo(Token.TOKNUMBER, lexeme, col_no)

            elif state == 2:
                      if self._is_index_within_range() and self.expr_str[self.current_pos].isdigit():
                          state = 3
                          lexeme += self.expr_str[self.current_pos]

                      else:
                            print("Error:Column {}: Number expected after '.' but found {}".format(self.current_pos + 1, self.expr_str[self.current_pos]))
                            return None


            elif state == 3:
                    if self._is_index_within_range and self.expr_str[self.current_pos].isdigit():
                        state = 3
                        lexeme += self.expr_str[self.current_pos]

                    else:
                        # again, assume this is state 4 and accept
                        self.current_pos -= 1
                        return TokenInfo(Token.TOKNUMBER, lexeme, col_no)


            self.current_pos += 1

        return  TokenInfo(Enum.TOKIDENT, lexeme, col_no)

    def _is_index_within_range(self):
        return self.current_pos < self.length_of_expr_str

if __name__ == "__main__":
        expr_str = "2    + 5.4 * / hell kofi_1 = 4.334334 % { } 45.h min(1, 4, 5) ?"
        tokenizer = Tokenizer(expr_str)
        token = tokenizer.get_next_token()
        print("\n\nThe input str is -> {}\n\n".format(expr_str))
        while token.token != Token.TOKEOLN:
            print("  Token: {0: <20}   Lexeme: {1: <20}   Col_no: {2: <10}".format(token.token, token.lexeme, token.col_no + 1))
            token = tokenizer.get_next_token()
