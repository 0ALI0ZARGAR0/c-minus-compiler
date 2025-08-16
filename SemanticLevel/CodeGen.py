from SemanticLevel.Assembler import Assembler, OPCode

# from SemanticLevel.SymbolTableV2 import SymbolTable  # Uncomment and implement as needed

class CodeGen:
    def __init__(self, data_address=500, temp_address=1000, stack_address=4000, runtime_stack_top=500):
        self.assembler = Assembler(data_address, temp_address, stack_address, runtime_stack_top)
        self.semantic_stack = []  # For values, addresses, temps, operators
        self.control_stack = []   # For labels, jump targets, break/continue
        # self.symbol_table = SymbolTable()  # Uncomment and implement as needed
        self.routines = {
            "#declare-var": self.declare_var,
            "#declare-array": self.declare_array,
            "#assign": self.assign,
            "#add": self.add,
            "#sub": self.sub,
            "#mult": self.mult,
            "#eq": self.eq,
            "#lt": self.lt,
            "#jpf": self.jpf,
            "#jp": self.jp,
            "#print": self.print_instruction,
            "#calc-arr-addr": self.calc_arr_addr,
            # Add more mappings as needed
        }

    # --- Semantic Stack Methods ---
    def ss_push(self, value):
        self.semantic_stack.append(value)

    def ss_pop(self):
        return self.semantic_stack.pop()

    # --- Control Stack Methods ---
    def cs_push(self, value):
        self.control_stack.append(value)

    def cs_pop(self):
        return self.control_stack.pop()

    # --- Array Declaration ---
    def declare_array(self, lookahead):
        # Assume lookahead provides array base address (from symbol table logic)
        array_base_addr = lookahead  # In practice, get from symbol table
        # Emit (ASSIGN, #0, <array_base_addr>, )
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.ASSIGN, f"#0", array_base_addr)
        self.ss_push(array_base_addr)

    # --- Array Element Address Calculation ---
    def calc_arr_addr(self, lookahead):
        # Pop index and base from stack
        index = self.ss_pop()
        base = self.ss_pop()
        # Step 1: MULT index, #4, temp1
        temp1 = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.MULT, index, "#4", temp1)
        # Step 2: ADD base, temp1, temp2
        temp2 = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.ADD, base, temp1, temp2)
        # Step 3: Use @temp2 for indirect addressing
        self.ss_push(f"@{temp2}")

    # --- Example Code Generation Methods ---
    def declare_var(self, lookahead):
        # TODO: Implement variable declaration logic using ss_push/ss_pop
        pass

    def assign(self, lookahead):
        rhs = self.ss_pop()
        lhs = self.ss_pop()
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.ASSIGN, rhs, lhs)
        self.ss_push(lhs)

    def add(self, lookahead):
        op2 = self.ss_pop()
        op1 = self.ss_pop()
        temp = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.ADD, op1, op2, temp)
        self.ss_push(temp)

    def sub(self, lookahead):
        op2 = self.ss_pop()
        op1 = self.ss_pop()
        temp = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.SUB, op1, op2, temp)
        self.ss_push(temp)

    def mult(self, lookahead):
        op2 = self.ss_pop()
        op1 = self.ss_pop()
        temp = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.MULT, op1, op2, temp)
        self.ss_push(temp)

    def eq(self, lookahead):
        op2 = self.ss_pop()
        op1 = self.ss_pop()
        temp = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.EQ, op1, op2, temp)
        self.ss_push(temp)

    def lt(self, lookahead):
        op2 = self.ss_pop()
        op1 = self.ss_pop()
        temp = self.assembler.temp_address
        self.assembler.move_temp_pointer(4)
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.LT, op1, op2, temp)
        self.ss_push(temp)

    def jpf(self, lookahead):
        cond = self.ss_pop()
        target = self.cs_pop()
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.JPF, cond, target)

    def jp(self, lookahead):
        target = self.cs_pop()
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.JP, target)

    def print_instruction(self, lookahead):
        value = self.ss_pop()
        self.assembler.add_instruction(len(self.assembler.program_block), OPCode.PRINT, value)
