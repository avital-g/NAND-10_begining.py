"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import numpy as np
import pandas as pd
NAME_T = "Name"
TYPE_T= "Type"
KIND_T= "Kind"
INDEX_T = "Index (#)"

STATIC = "static"
FIELD_T = "field"
ARG ="arg"
VAR="var"


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_table = pd.DataFrame(columns= [NAME_T, TYPE_T, KIND_T, INDEX_T])
        self.subroutine_table = pd.DataFrame(columns=[NAME_T, TYPE_T, KIND_T, INDEX_T])
        self.value_count_dict ={ARG:0, VAR: 0 ,STATIC:0, FIELD_T:0 }

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = pd.DataFrame(columns=[NAME_T, TYPE_T, KIND_T, INDEX_T])



    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        #table = None
        if kind in [STATIC, FIELD_T]:
            table = self.class_table
        else:
            table = self.subroutine_table
        var_index = self.value_count_dict[kind]
        table= table.append({NAME_T:name,TYPE_T:type,KIND_T:kind,INDEX_T:var_index}, ignore_index=True)
        self.value_count_dict[kind]+=1
        if kind in [STATIC, FIELD_T]:
            self.class_table =table
        else:
            self.subroutine_table = table

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.value_count_dict[kind]

    def get_a_property_from_table (self,property: str, name: str):
        information = self.subroutine_table.loc[self.subroutine_table[NAME_T] == name]
        if information.empty:
            information = self.class_table[self.class_table[NAME_T] == name]
        if information.empty:
            print("**\n\n\n error: can't find symbol\n\n\n")
        return information[property].item()


    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        return self.get_a_property_from_table(KIND_T,name)



    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        return self.get_a_property_from_table(TYPE_T,name)

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        return int( self.get_a_property_from_table(INDEX_T,name))
