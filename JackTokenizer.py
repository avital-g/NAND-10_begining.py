"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


import typing


KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"

INTCONST = "integerConstant"
STRINGCONST ="stringConstant"


keyword_list = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char","boolean",
                "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]

symbol_list =["{","}","(",")","[","]",".",",",";",
              "+","-","*","/","&","|","<",">","=","~"]

line_breakers = ["//","/*","*/"]


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.last_token = None
        self.input_lines = input_stream.read().splitlines()
        self.number_of_lines = len(self.input_lines)
        self.current_line_number = 0
        self.current_token = None
        self.current_token_type = None
        self.current_line = self.handle_line_reading(self.input_lines[0])
        self.is_comment = False




    def handle_line_reading(self, origionael_line:str):
        line = origionael_line.strip()
        for breaker in line_breakers:
            if breaker in line:
                if breaker =="/*":
                    line_breakers.append("*")
                if "*/" in line and "*" in line_breakers:
                    line_breakers.remove("*")
                    line = ""
                    break
                spliting = line.split(breaker)
                if spliting[0] != "":
                    line = spliting[0]
                else:
                    line = ""
                break

        return line.strip("\t ")


    def is_this_end_of_line(self):
        if len( self.handle_line_reading(self.current_line))==0:
            return True
        return False


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.current_line_number == self.number_of_lines-1:
            return not self.is_this_end_of_line()
        return True

    def recognize_next_token(self) -> int:
        token_end = 0
        if len (self.current_line) == 0:
            return 0
        for keyword in keyword_list:
            if self.current_line.startswith(keyword):
                self.current_token = keyword
                self.current_token_type = KEYWORD
                token_end = len (keyword)
                return token_end

        for symbol in symbol_list:
            if self.current_line.startswith(symbol):
                self.current_token = symbol
                self.current_token_type = SYMBOL
                token_end = len (symbol)
                return token_end

        if self.current_line[0].isnumeric():
            index = 1
            while index < len(self.current_line) and self.current_line[0:index].isnumeric():
                index += 1
            self.current_token= self.current_line[0:index-1]
            self.current_token_type = INTCONST
            token_end = index-1
            return token_end

        elif self.current_line[0] == "\"":
            index = 1
            while index < len(self.current_line) and self.current_line[index] != "\"":
                index += 1
            self.current_token = self.current_line [ 1: index]
            self.current_token_type = STRINGCONST
            token_end = index+1
            return token_end
        else:
            index = 1
            while index < len(self.current_line) and self.current_line[index] not in symbol_list+[" ","\t","\n"]:
                index +=1
            self.current_token =self.current_line[0:index]
            self.current_token_type = IDENTIFIER
            token_end = index
        return token_end





    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!

        self.current_line = self.handle_line_reading(self.current_line)
        while self.is_this_end_of_line() and self.has_more_tokens():
            self.current_line_number += 1
            self.current_line = self.input_lines[self.current_line_number]
            self.current_line = self.handle_line_reading(self.current_line)
        if not self.has_more_tokens():
            return

        self.last_token = self.current_token
        token_end = self.recognize_next_token()
        if token_end < len (self.current_line):
            self.current_line = self.current_line[token_end:]
        else:
            self.current_line= ""


    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        return self.current_token_type

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return self.current_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.current_token
