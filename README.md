# spell-checker

Description

The evaluator is based on the grammar specific in the EBNF notation below:


Expr				 --> AddExpr\
AddExpr			 --> MulExpr { ("+" | "-") MulExpr }\
MulExpr			 --> UnaryExpr { ("*" | "/" | "%") UnaryExpr }\
UnaryExpr		 --> PrimaryExpr\
				        | ("+" | "-") UnaryExpr\
PrimaryExpr  --> number\
				        | Ident\
				        | Ident "(" [ Expr { "," Expr } ] ")"\
                | Ident ":=" Expr\
				        | "(" Expr ")"\
Ident				 --> "a" - "z" {"a" - "z" "0" - "9" "_"}\
number			 --> integer\
				        | real\
integer			 --> "0" - "9" {"0" - "9"}\
real				 --> integer "." integer\



## Installation

Clone project here https://github.com/Arkatgit/expression-evaluator-python.git

## Usage


    $ python main.py


## Examples

...

### Bugs

...

### Any Other Sections
### That You Think
### Might be Useful

## License
