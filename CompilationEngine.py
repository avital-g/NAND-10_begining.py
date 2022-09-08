"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

#

## statements
LET_STAT= "letStatement"
IF_STAT = "ifStatement"
WHILE_STAT ="whileStatement"
DO_STAT = "doStatement"
RETURN_STAT = "returnStatement"

statement_flags = [LET_STAT, IF_STAT, WHILE_STAT, DO_STAT, RETURN_STAT]

##
CLASS_DEC = "class"
CLASS_VAR_DEC = "classVarDec"
SUBROUTINE_BODY = "subroutineBody"
SUBROUTINE_DEC = "subroutineDec"
VAR_DEC= "varDec"

PARAMETER_LIST_FLAG = "parameterList"
STATEMENTS_FLAG = "statements"
TERM = "term"
EXPRESSION = "expression"

EXPRESSION_LIST ="expressionList"
KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"

INTCONST = "integerConstant"
STRINGCONST ="stringConstant"


STATIC ="static"
FIELD = "field"
VAR ="var"
ARG = "arg"

CONSTRUCTOR ="constructor"
FUNCTION = "function"
METHOD= "method"
RETURN_STAT = "returnStatement"

COMMA = ","
DOT_COMMA =";"

LET="let"
DO="do"
IF= "if"
ELSE= "else"
WHILE = "while"
RETURN =  "return"


##STATIC defined above
LOCAL = "local"
ARGUMENT_SEG = "argument"
THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"
CONSTANT = "constant"


keyword_extended = [KEYWORD,IDENTIFIER]
statements = [LET, DO,IF,WHILE,RETURN]



class_var_dec_openers = [STATIC,FIELD]
subroutine_openers = [CONSTRUCTOR, FUNCTION,METHOD]
type_var_names = ["int", "char","boolean","void"]
keyword_list = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char","boolean",
                "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]

symbol_list =["{","}","(",")","[","]",".",",",";",
              "+","-","*","/","&","|","<",">","=","~"]

op_list = ["+","-","*","/","&","|","<",">","=","~"]

term_openers = [INTCONST,STRINGCONST,IDENTIFIER,"true", "false", "null", "this"]
parenthesis_openers = ["[","("]
parenthesis_closers = ["]",")"]
unary_op = ["~","-"]

symbol_dict = {"<":"&lt;", ">":"&gt;", "\"":"&quot;", "&":"&amp;"}
names_to_segments ={VAR: LOCAL, ARG: ARGUMENT_SEG, STATIC: STATIC, FIELD: THIS}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output_stream  = output_stream
        self.num_of_tabs =0
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.vmWriter =  VMWriter(output_stream)

    def token_flag(self, token_type):
        return "<"+token_type+">"

    def basic_line(self, token, token_type):
        token_text= token
        if token in symbol_dict.keys():
            token_text = symbol_dict[token]

        to_write = self.token_flag(token_type)+" "+token_text+" "+self.token_flag("/"+token_type)
        return to_write

    def write_XML(self, to_write):

        print(to_write+"\n")
        #self.output_stream.write(to_write+"\n")

    def process(self, expected_token ):
        if self.tokenizer.current_token != expected_token:
            print("synthax error: line " +str( self.tokenizer.current_line_number) + "\n"
                                                                                "expected:" + expected_token + "\n"
                                                                                                               "actual: " + self.tokenizer.token_type())
        else :
            self.write_XML(self.basic_line(expected_token, self.tokenizer.token_type()))
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def process_basic_token(self, expected_token_type):
        if expected_token_type != self.tokenizer.token_type():
            print("synthax error: line " + str(self.tokenizer.current_line_number) +"\n"
                                                                            "expected:" + expected_token_type +"\n"
                                                                                                             "actual: " + self.tokenizer.token_type())

        self.write_XML(self.basic_line(self.tokenizer.current_token, self.tokenizer.token_type()))
        self.tokenizer.advance()

    def process_optional_tokens(self, expected_list_of_tokens: list):
        if self.tokenizer.token_type() not in expected_list_of_tokens and self.tokenizer.current_token not in expected_list_of_tokens :
            print("synthax error: line " +str( self.tokenizer.current_line_number) + "\n"
                                                                                "expected:" )
            print(expected_list_of_tokens)
            print ("\n actual: " + self.tokenizer.token_type())

        self.write_XML(self.basic_line(self.tokenizer.current_token, self.tokenizer.token_type()))
        self.tokenizer.advance()

    def open_seq (self, seq):
        title = self.token_flag(seq)
        #print(title)
        self.write_XML(title)

    def close_seq (self, seq):
        self.open_seq("/"+seq)

    """project 10 additions:"""

    def write_to_ST(self, names, type, kind):
        for name in  names:
            self.symbol_table.define(name,type,kind)

    def find_variable_in_st(self, variable_name):
        """

        Args:
            variable_name: the name of the variable called

        Returns: the segment and index such as "argument", "1"

        """
        type = self.symbol_table.type_of(variable_name)
        index = self.symbol_table.index_of(variable_name)
        return names_to_segments[type], index

    def compile_class(self) -> None:
        """Compiles a complete class."""

        self.open_seq(CLASS_DEC)
        self.process("class")
        self.class_name = self.tokenizer.current_token
        self.process_basic_token(IDENTIFIER)
        self.process("{")
        ## note -make sure it can be complied several times
        while self.tokenizer.current_token in class_var_dec_openers:
            self.compile_class_var_dec()
        while self.tokenizer.current_token in subroutine_openers:
            self.compile_subroutine()
        self.process("}")
        self.close_seq(CLASS_DEC)


    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.open_seq(CLASS_VAR_DEC)
        ##process the field/static
        kind = self.tokenizer.current_token
        self.process_basic_token(KEYWORD)
        ## the type
        type = self.tokenizer.current_token
        self.process_optional_tokens(keyword_extended)

        identifiers_list =[]
        identifiers_list.append(self.tokenizer.current_token)
        self.process_basic_token(IDENTIFIER)
        while self.tokenizer.current_token == COMMA:
            self.process_basic_token(SYMBOL)
            identifiers_list.append(self.tokenizer.current_token)
            self.process_basic_token(IDENTIFIER)
        self.process(";")
        self.write_to_ST(identifiers_list,type,kind)
        self.close_seq(CLASS_VAR_DEC)


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.open_seq(SUBROUTINE_DEC)
        ##restarting the subtoutine symbol-table
        self.symbol_table.start_subroutine()
        self.process_basic_token(KEYWORD)
        self.process_optional_tokens(keyword_extended)
        self.process_basic_token(IDENTIFIER)
        self.process("(")
        self.compile_parameter_list()
        self.process(")")
        self.compile_subroutine_body()
        self.close_seq(SUBROUTINE_DEC)


    def compile_subroutine_body(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.open_seq(SUBROUTINE_BODY)
        self.process("{")
        while self.tokenizer.current_token ==VAR:
            self.compile_var_dec()
        self.compile_statements()
        self.process("}")
        self.close_seq(SUBROUTINE_BODY)


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.open_seq(PARAMETER_LIST_FLAG)
        parameters =[]
        types =[]
        while self.tokenizer.current_token != ")":
            types.append(self.tokenizer.identifier())
            self.process_basic_token(KEYWORD)
            parameters.append(self.tokenizer.keyword())
            self.process_basic_token(IDENTIFIER)
            if self.tokenizer.current_token == COMMA:
                self.process(COMMA)
        for param in range(len(parameters)):
            self.symbol_table.define(parameters[param],types[param],ARG)
        self.close_seq(PARAMETER_LIST_FLAG)


    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.open_seq(VAR_DEC)
        self.process(VAR)
        type= self.tokenizer.keyword()

        self.process_optional_tokens([KEYWORD,IDENTIFIER])
        names=[]
        names.append(self.tokenizer.identifier())
        self.process_basic_token(IDENTIFIER)
        while self.tokenizer.current_token == COMMA:
            self.process(COMMA)
            names.append(self.tokenizer.identifier())
            self.process_basic_token(IDENTIFIER)
        self.process(";")
        self.write_to_ST(names,type,VAR)
        self.close_seq(VAR_DEC)


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.open_seq(STATEMENTS_FLAG)
        while self.tokenizer.current_token in statements:
            token =self.tokenizer.current_token
            if token == LET:
                self.compile_let()
            elif token == WHILE:
                self.compile_while()
            elif token == IF:
                self.compile_if()
            elif token == DO:
                self.compile_do()
            elif token == RETURN:
                self.compile_return()
                break
        self.close_seq(STATEMENTS_FLAG)


    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.open_seq(DO_STAT)

        self.process(DO)
        self.compile_subroutine_call()
        self.process(";")
        self.close_seq(DO_STAT)


    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.open_seq(LET_STAT)
        self.process(LET)
        self.process_basic_token(IDENTIFIER)
        while self.tokenizer.current_token == "[":
            self.process("[")
            self.compile_expression()
            self.process("]")
        self.process("=")
        self.compile_expression()
        self.process(";")
        self.close_seq(LET_STAT)


    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.open_seq( WHILE_STAT )
        self.process("while")
        self.process("(")
        self.compile_expression()
        self.process(")")
        self.process("{")
        self.compile_statements()
        self.process("}")
        self.close_seq(WHILE_STAT)


    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.open_seq(RETURN_STAT)

        self.process(RETURN)
        if self.tokenizer.current_token!=";":
            self.compile_expression()
        self.process(DOT_COMMA)
        self.close_seq(RETURN_STAT)


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.open_seq(IF_STAT)

        self.process(IF)
        self.process("(")
        self.compile_expression()
        self.process( ")" )
        self.process("{")
        self.compile_statements()
        self.process("}")
        while self.tokenizer.current_token ==ELSE:
            self.process(ELSE)
            self.process("{")
            self.compile_statements()
            self.process("}")
        self.close_seq(IF_STAT)


    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.open_seq(EXPRESSION)
        if self.tokenizer.current_token not in parenthesis_closers:
            self.compile_term()
        while self.tokenizer.current_token in op_list:
            self.process_optional_tokens(op_list)
            self.compile_term()
        self.close_seq(EXPRESSION)


    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        self.open_seq(TERM)
        if self.tokenizer.current_token in parenthesis_openers:
            self.process_optional_tokens(parenthesis_openers)
            self.compile_expression()
            self.process_optional_tokens(parenthesis_closers)
            self.close_seq(TERM)
            return
        if self.tokenizer.current_token in unary_op:
            self.process_optional_tokens(unary_op)
            self.compile_term()
            self.close_seq(TERM)
            return
        if self.tokenizer.current_token not in parenthesis_openers:
            self.process_optional_tokens(term_openers)
            if self.tokenizer.current_token == ".":
                self.process(".")
                self.process_basic_token(IDENTIFIER)
        ## turn into subroutine call
        while self.tokenizer.current_token in parenthesis_openers:
            type =  self.tokenizer.current_token
            self.process_optional_tokens(parenthesis_openers)
            if type == "(":
                self.compile_expression_list()
            elif type == "[":
                self.compile_expression()
            self.process_optional_tokens(parenthesis_closers)
        self.close_seq(TERM)


    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.open_seq(EXPRESSION_LIST)
        while self.tokenizer.current_token != ")":
            self.compile_expression()
            if self.tokenizer.current_token == COMMA:
                self.process(COMMA)
            else:
                break
        self.close_seq(EXPRESSION_LIST)


    def compile_subroutine_call(self)->None:
        self.process_basic_token(IDENTIFIER)
        if self.tokenizer.current_token == ".":
            self.process(".")
            self.process_basic_token(IDENTIFIER)
        self.process("(")
        self.compile_expression_list()
        self.process(")")


























