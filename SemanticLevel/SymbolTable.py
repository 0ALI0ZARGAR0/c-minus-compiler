from SemanticLevel.ErrorType import ErrorTypeEnum, error

last_adr = 508  # Start arrays at 508 as per project requirements
symbol_table_instance = None


class SymbolTableClass:
    scope_stack = []
    pars_table = []
    next_var_addr = 528  # Start variables at 528
    next_arr_addr = 508  # Start arrays at 508

    @staticmethod
    def get_instance():
        global symbol_table_instance
        if symbol_table_instance is None:
            symbol_table_instance = SymbolTableClass()
        return symbol_table_instance

    def add(self, row):
        global last_adr
        # Determine if this is an array or a variable
        if hasattr(row, 'is_arr') and getattr(row, 'is_arr', False):
            # Allocate array at next_arr_addr, but do NOT increment here
            row.address = SymbolTableClass.next_arr_addr
        else:
            # Allocate variable at next_var_addr
            row.address = SymbolTableClass.next_var_addr
            SymbolTableClass.next_var_addr += 4
        self.pars_table.append(row)
        # can handle zero input count function?? amir
        if row.category == "param":
            if self.pars_table[self.pars_table.__len__() - 2].category == "var":
                self.pars_table[self.pars_table.__len__() -
                                2].category = "func"

    def get_row(self, lexeme, adr=False):
        for i in range(self.pars_table.__len__()):
            if not adr:
                if self.pars_table[self.pars_table.__len__() - 1 - i].lexeme == lexeme:
                    return self.pars_table[self.pars_table.__len__() - 1 - i]
            else:
                if self.pars_table[self.pars_table.__len__() - 1 - i].address == lexeme:
                    return self.pars_table[self.pars_table.__len__() - 1 - i]

    def set_last_args(self, args, arr_temp):
        global last_adr
        # Update array address to reserve a block for the array
        arr_row = self.pars_table[self.pars_table.__len__() - 1]
        arr_row.args_cells = args
        arr_row.is_arr = True
        arr_row.temp_start_pos = arr_row.address  # base address is the array's address
        # Reserve space for the array
        SymbolTableClass.next_arr_addr += 4 * args

    def set_line_category(self, line, c):
        for row in self.pars_table:
            if row.line == line:
                row.category = c

    def remove_scope(self, scope):
        length = self.pars_table.__len__()
        for i in range(length):
            if self.pars_table[length - 1 - i].scope == scope:
                self.pars_table.pop()
            else:
                return

    def is_lexeme(self, address):
        row = self.get_row(address, adr=True)
        return row is not None

    def get_category(self, lexeme, adr=False):
        # return var or func
        row = self.get_row(lexeme, adr=adr)
        if row is not None:
            return row.category

    def inc_func_args(self, row):
        for i in range(self.pars_table.__len__()):
            if self.pars_table[self.pars_table.__len__() - 1 - i].category == "func":
                self.pars_table[self.pars_table.__len__() - 1 -
                                i].args_cells += 1
                self.pars_table[self.pars_table.__len__(
                ) - 1 - i].params_type.append(row)
                return

    def get_adr(self, lexeme):
        for i in range(self.pars_table.__len__()):
            if self.pars_table[self.pars_table.__len__() - 1 - i].lexeme == lexeme:
                return self.pars_table[self.pars_table.__len__() - 1 - i].address

    def get_arr_temp(self):

        arr_addr = self.pars_table[self.pars_table.__len__() - 1].address
        arr_tmp_start = self.pars_table[self.pars_table.__len__(
        ) - 1].temp_start_pos
        return arr_tmp_start, arr_addr

    def get_arr_base_address(self, arr_id):
        """Get the actual base address (temp_start_pos) of an array by its variable address"""
        for i in range(self.pars_table.__len__()):
            if self.pars_table[self.pars_table.__len__() - 1 - i].address == int(arr_id):
                return self.pars_table[self.pars_table.__len__() - 1 - i].temp_start_pos
        return arr_id  # fallback to original if not found

    def set_starting_line(self, line):
        self.pars_table[self.pars_table.__len__() - 1].starting_line = line

    def get_starting_line(self, lexeme, by_adr=False):
        for i in range(self.pars_table.__len__()):
            if not by_adr:
                if self.pars_table[self.pars_table.__len__() - 1 - i].lexeme == lexeme:
                    return self.pars_table[self.pars_table.__len__() - 1 - i].starting_line
            else:
                adr = int(lexeme)
                if self.pars_table[self.pars_table.__len__() - 1 - i].address == adr:
                    return self.pars_table[self.pars_table.__len__() - 1 - i].starting_line

    def find_adrs(self):
        adrs = []
        last_scope = -1
        for i in range(self.pars_table.__len__()):
            if last_scope == -1:
                last_scope = self.pars_table[self.pars_table.__len__(
                ) - 1 - i].scope
            if last_scope != self.pars_table[self.pars_table.__len__() - 1 - i].scope:
                return adrs
            if self.pars_table[self.pars_table.__len__() - 1 - i].category != "func":
                adrs.append(
                    self.pars_table[self.pars_table.__len__() - 1 - i].address)
        return adrs

    def get_func_args(self):
        for i in range(self.pars_table.__len__()):
            if self.pars_table[self.pars_table.__len__() - 1 - i].category == "func":
                return self.pars_table[self.pars_table.__len__() - 1 - i].args_cells

    def check_void_var(self):
        for row in self.pars_table:
            if row.category == "var" and row.type == "void" and not row.err_wrote:
                row.err_wrote = True
                error(ErrorTypeEnum.void_type, row.lexeme)


class SymbolRow:
    address = 0
    lexeme = ""
    args_cells = 0
    type = ""
    scope = ""
    params_type = [].copy()
    starting_line = 0
    line = 0
    temp_start_pos = 0
    # func, var
    category = ""
    err_wrote = False

    def __init__(self):
        self.address = 0
        self.lexeme = ""
        self.args_cells = 0
        self.type = ""
        self.scope = ""
        self.params_type = [].copy()
        self.starting_line = 0
        self.line = 0
        self.temp_start_pos = 0
        # func, var
        self.category = ""
        self.err_wrote = False
        self.is_arr = False

    def __str__(self):
        return "address: " + str(self.address) + " lexeme: " + self.lexeme + " scope: " + str(self.scope)


class FuncCallBlock:
    call_params = []
    function_row = None
    read_param = True

    def __init__(self, func_row):
        self.function_row = func_row
        self.call_params = []
        self.read_param = True
        self.start_param = False

    def add_param_row(self, row):
        if not self.call_params.__contains__(row) and self.read_param:
            self.call_params.append(row)
            self.read_param = False

    def next_param(self):
        self.read_param = True
