import logging
from tokenizer import Tokenizer, Token
from symtab import sym_tab

logger = logging.getLogger(__name__)


"""
Reccursive descent parser for the grammar

Expr			 --> AddExpr
AddExpr			 --> MulExpr { ("+" | "-") MulExpr }
MulExpr			 --> UnaryExpr { ("*" | "/" | "%") UnaryExpr }
UnaryExpr		 --> PrimaryExpr
				     | ("+" | "-") UnaryExpr
PrimaryExpr  --> number
				        | Ident
				        | Ident "(" [ Expr { "," Expr } ] ")"
                        | Ident ":=" Expr
				        | "(" Expr ")"
Ident				 --> "a" - "z" {"a" - "z" "0" - "9" "_"}
number			 --> integer
				        | real
integer			 --> "0" - "9" {"0" - "9"}
real				 --> integer "." integer

"""

class Parser():
    def __init__(self, expr_str: str):
        self.tokenizer = Tokenizer(expr_str)

    def parse(self) -> float:
        self.tok = self.tokenizer.get_next_token()
        return self._Expr()

    def _Expr(self) -> float:
        """
            Expr  --> AddExpr
        """
        logger.debug("In Expr with {}".format(self.tok.lexeme))
        result = 0 
        # Check for first set
        if self.tok.token in [Token.TOKPLUS, Token.TOKMINUS, Token.TOKIDENT, Token.TOKLPAREN, Token.TOKNUMBER]:
            result = self._AddExpr()
        else:
            logger.error("Error:Column {}: '{}' is not a valid start of an expression".format(self.tok.col_no + 1, self.tok.lexeme))
        logger.debug("Leaving Expr with {}".format(self.tok.lexeme))
        return result
    def _AddExpr(self) -> float:
        """
            AddExpr	 --> MulExpr { ("+" | "-") MulExpr }
        """
        logger.debug("In AddExpr with {}".format(self.tok.lexeme))

        lval = self._MulExpr()
        while self.tok.token == Token.TOKPLUS or self.tok.token == Token.TOKMINUS:
            tok = self.tok.token
            self.tok = self.tokenizer.get_next_token()
            lval = lval + self._MulExpr() if tok == Token.TOKPLUS else lval - self._MulExpr()

        logger.debug("Leaving AddExpr with {}".format(self.tok.lexeme))
        return lval

    def _MulExpr(self) -> float:
        """
            MulExpr	--> UnaryExpr { ("*" | "/" | "%") UnaryExpr }
        """
        logger.debug("In MulExpr with {}".format(self.tok.lexeme))

        lval = self._UnaryExpr()
        while self.tok.token == Token.TOKMUL or self.tok.token == Token.TOKDIVIDE or self.tok.token == Token.TOKMOD:
            tok = self.tok.token
            self.tok = self.tokenizer.get_next_token()
            rval = self._UnaryExpr()
            if tok == Token.TOKMUL:
                lval *= rval
            elif tok == Token.TOKDIVIDE:
                lval /= rval
            else:
                lval %= rval

        logger.debug("Leaving MulExpr with {}".format(self.tok.lexeme))
        return lval

    def _UnaryExpr(self) -> float:
        """
        UnaryExpr   --> PrimaryExpr
        			| ("+" | "-") UnaryExpr
        """
        logger.debug("In UnaryExpr with {}".format(self.tok.lexeme))
        result = 0
        if self.tok.token == Token.TOKIDENT or self.tok.token == Token.TOKNUMBER or self.tok.token == Token.TOKLPAREN:
            result = self._PrimaryExpr()

        elif self.tok.token == Token.TOKPLUS or self.tok.token == Token.TOKMINUS:
            tok = self.tok.token
            self.tok = self.tokenizer.get_next_token()
            result = self._UnaryExpr() if tok == Token.TOKPLUS else -1 * self._UnaryExpr()

        else:
            logger.error("Error:Column {}: '{}' is an invalid start of a unary expression".format(self.tok.col_no + 1, self.tok.lexeme))
            #Incase of error, just report and maintain default 0 for result

        logger.debug("Leaving UnaryExpr with {}".format(self.tok.lexeme))
        return result

    def _PrimaryExpr(self) -> float:
        """
        PrimaryExpr  --> number
        				        | Ident
        				        | Ident "(" [ Expr { "," Expr } ] ")"
                                | Ident "=" Expr
        				        | "(" Expr ")"
        """
        logger.debug("In PrimaryExpr with {}".format(self.tok.lexeme))
        result = 0
        if self.tok.token == Token.TOKNUMBER:
            result = float(self.tok.lexeme)
            self.tok = self.tokenizer.get_next_token()


        elif self.tok.token == Token.TOKIDENT:
            ident_lexeme = self.tok.lexeme
            col_no = self.tok.col_no
            is_defined = ident_lexeme in sym_tab
            is_var_access = True

            self.tok = self.tokenizer.get_next_token()

            if self.tok.token == Token.TOKLPAREN:
                arg_list = []
                self.tok = self.tokenizer.get_next_token()
                exp = self._Expr()
                arg_list.append(exp)

                while self.tok.token == Token.TOKCOMMA:
                    self.tok = self.tokenizer.get_next_token()
                    exp = self._Expr()
                    arg_list.append(exp)

                if self.tok.token == Token.TOKRPAREN:

                    if is_defined:
                        result = sym_tab[ident_lexeme](*arg_list)
                    else:
                        logger.error("Error:Column {}: '{}' is not part of the predefined functions".format(col_no + 1, ident_lexeme))

                    is_var_access = False

                    self.tok = self.tokenizer.get_next_token()


                else:
                    logger.error("Error:Column {}: ')' expected before '{}'".format(self.tok.col_no + 1, self.tok.lexeme))

            elif self.tok.token == Token.TOKEQUAL:
                self.tok = self.tokenizer.get_next_token()
                result = self._Expr()
                #add variable to symbol table
                sym_tab[ident_lexeme] = result
                is_var_access = False

            if is_var_access == True:
                if not is_defined:
                    logger.error("Error:Column {}: the variable '{}' is not defined".format(col_no + 1, ident_lexeme))

                else:
                    result = sym_tab[ident_lexeme]

        elif self.tok.token == Token.TOKLPAREN:
            self.tok = self.tokenizer.get_next_token()
            result = self._Expr()
            if self.tok.token == Token.TOKRPAREN:
                self.tok = self.tokenizer.get_next_token()
            else:
                logger.error("Error:Column {}: ')' expected before '{}'".format(self.tok.col_no + 1, self.tok.lexeme))

        logger.debug("Leaving PrimaryExpr with {}".format(self.tok.lexeme))
        return result

def repl(prompt: str = "Expr-> ") -> str:
    while True:
        expr_str = input(prompt)
        if expr_str == "quit":
            return
        parser = Parser(expr_str)
        print("Ans:-> {}".format(parser.parse()))


if __name__ == '__main__':
	logging.basicConfig(level=logging.ERROR)
	repl()
