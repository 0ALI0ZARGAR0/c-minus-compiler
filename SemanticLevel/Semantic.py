import SemanticLevel.ErrorType
import SemanticLevel.SymbolTable
from SemanticLevel import ErrorType, SemanticRoutines
from SemanticLevel.ErrorType import ErrorTypeEnum
from SemanticLevel.SymbolTable import SymbolTableClass
from Tools.Development import develop_mode

semantic_instance = None
temp_instance = None


class TempManager:
    """Manages temporary address allocation for TAC generation.

    The manager allocates aligned integer addresses by increasing a
    counter by a fixed stride (word size) for each new temporary.
    """
    current_temp = 0
    increase_amount = 0

    @staticmethod
    def get_instance():
        return temp_instance

    def __init__(self, current_temp=None, increase_amount=4):
        global temp_instance
        # Always start temps at the next available variable address
        from SemanticLevel.SymbolTable import SymbolTableClass
        if current_temp is None:
            self.current_temp = SymbolTableClass.next_var_addr
        else:
            self.current_temp = current_temp
        self.increase_amount = increase_amount
        temp_instance = self

    def get_temp(self):
        """Return the next available temporary address."""
        self.current_temp += self.increase_amount
        return self.current_temp

    def get_arr_temp(self, arr_len):
        """Reserve a contiguous block of temporaries for an array.

        Args:
            arr_len: Number of integer cells to reserve.

        Returns:
            The starting address of the reserved block.
        """
        self.current_temp += self.increase_amount
        start_point = self.current_temp
        self.current_temp += self.increase_amount * (arr_len - 1)
        return start_point


class Semantic:
    """Semantic driver which dispatches action symbols to routines.

    This class holds references to the symbol table and the temp manager
    and exposes a `run` method to be called by the parser for each
    action symbol (prefixed with '#').
    """
    name_function_dict = {
    }
    parse_table = None
    temp_manager = None
    errors = []

    @staticmethod
    def get_instance():
        """Return the singleton `Semantic` instance."""
        global semantic_instance
        if semantic_instance is None:
            semantic_instance = Semantic(
                SemanticLevel.SymbolTable.SymbolTableClass.get_instance())
        return semantic_instance

    def __init__(self, pars_table):
        global semantic_instance
        self.parse_table = pars_table
        self.temp_manager = TempManager(1500, 4)
        semantic_instance = self
        if develop_mode:
            print(r"    {:30} {:15} {}".format(
                "func_name", "input_token", "Semantic Stack"))

    def run(self, func_name, input_token):
        """Execute the semantic routine named by `func_name`.

        Args:
            func_name: Name of the action (e.g., '#assign').
            input_token: The raw token value associated with the action.
        """
        if develop_mode:
            print(
                r"==> {func_name:30} {input_token:15} {SemanticRoutines}".
                format(func_name=func_name[1:], input_token=input_token,
                       SemanticRoutines=SemanticRoutines.semantic_stack))
        func_name = func_name[1:len(func_name)]
        getattr(SemanticRoutines, "func_" +
                func_name)(self.temp_manager.get_temp, input_token)
