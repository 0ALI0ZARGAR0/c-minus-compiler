# For test
from Parser import DFA
from Parser.grammer_to_transition import fill_nterminal_id_dict, rule_to_states
from SemanticLevel import Semantic, SymbolTable
from SemanticLevel.ErrorType import error, semantic_errors
from SemanticLevel.Semantic import TempManager
from SemanticLevel.SemanticRoutines import program_block
from Tools.Development import develop_mode


def pp_list_of_tuples(lsot):
    f = open("output.txt", "w")
    s = ""
    if develop_mode:
        print("\n[")
    if semantic_errors.__len__() > 0:
        s = "The output code has not been generated"
    else:
        for idx, t in enumerate(lsot):
            s += f"{idx}\t{t}\n"
            if develop_mode:
                pass
                print(r"{idx:3}: {t}".format(idx=idx, t=t))
    if develop_mode:
        print("]")
    f.write(s)


# Main imports

errors = []
# f = open("c-minus_001 (1).txt", "r")
# f = open("test_grammer", "r")
line_counter = 1
# Prefer loading grammar from file for maintainability
try:
    with open("Parser/grammer.txt", "r", encoding="utf-8") as _gfile:
        _lines = [ln.strip() for ln in _gfile.readlines() if ln.strip()]
        grammar = "@".join(_lines)
except Exception:
    grammar = \
        "Program -> Declaration-list #at_the_end $@Declaration-list -> Declaration Declaration-list | EPSILON@Declaration -> Declaration-initial Declaration-prime@Declaration-initial ->  Type-specifier #pid ID@Declaration-prime -> #save_first_func Fun-declaration-prime | Var-declaration-prime @Var-declaration-prime -> #set_tmp_value ; | [ NUM ] #set_tmp_addr #pop ;@Fun-declaration-prime ->  #set_starting_line ( Params ) #declaration_after_header Compound-stmt #push_zero #declaration_after_return #after_func_declaration@Type-specifier -> int | void@Params -> int #pid ID Param-prime Param-list | void@Param-list -> , Param Param-list | EPSILON@Param -> Declaration-initial Param-prime@Param-prime -> [  ] | EPSILON@Compound-stmt -> { Declaration-list Statement-list }@Statement-list -> Statement Statement-list | EPSILON@Statement -> Expression-stmt | Compound-stmt | Selection-stmt | Iteration-stmt | Return-stmt | output ( Expression #output ) ;@Expression-stmt -> Expression ; #pop | #break break ; | ;@Selection-stmt -> if ( Expression ) #save Statement Else-stmt@Else-stmt -> #jpf | else #jpf_save Statement #jp@Iteration-stmt -> repeat #label Statement until ( Expression ) #until | while #label ( Expression ) #while_jpf Statement #while_jp_back@Return-stmt -> return Return-stmt-prime @Return-stmt-prime -> #push_zero #declaration_after_return ; | Expression #declaration_after_return ;@Expression -> Simple-expression-zegond | #pid ID B@B -> = Expression #assign | [ Expression #parr ] H | Simple-expression-prime@H -> = Expression #assign | G D C@Simple-expression-zegond -> Additive-expression-zegond C@Simple-expression-prime -> Additive-expression-prime C@C -> #push Relop Additive-expression #comp_op | EPSILON@Relop -> < | ==@Additive-expression -> Term D@Additive-expression-prime -> Term-prime D@Additive-expression-zegond -> Term-zegond D@D ->  #push Addop Term #add_op D | EPSILON@Addop -> + | -@Term -> Factor G@Term-prime -> Factor-prime G@Term-zegond -> Factor-zegond G@G -> * Factor #mult_op G | EPSILON@Factor -> ( Expression ) | #pid ID Var-call-prime | #pnum NUM@Var-call-prime -> ( #call_begin Args #call_end ) | Var-prime@Var-prime -> [ Expression #parr ] | EPSILON@Factor-prime -> ( #call_begin Args #call_end ) | EPSILON@Factor-zegond -> ( Expression ) | #pnum NUM@Args -> Arg-list | EPSILON@Arg-list -> Expression #call_add_args Arg-list-prime@Arg-list-prime -> , Expression #call_add_args Arg-list-prime | EPSILON"

fill_nterminal_id_dict(grammar)
for line in grammar.split("@"):
    rule_to_states(DFA.State, line)


f = open("input.txt", "r")
for line in f:
    line_counter += 1
try:
    DFA.states_stack.append(DFA.nterminal_first_state['Program'])
except KeyError:
    raise RuntimeError("Start symbol 'Program' not found in DFA.nterminal_first_state. Check your grammar and DFA initialization.")
# DFA.states_stack.append(DFA.nterminal_first_state['P'])
symbol_row = SymbolTable.SymbolRow()
symbol_table = SymbolTable.SymbolTableClass.get_instance()
semantic = Semantic.Semantic.get_instance()
active_row = False

brackets = list()
no_bracket_function = False
scope = 0
gl_line_number = 0
func_declare_started = False
func_call_table_list = []
func_in_call = False

arrays_stack = []


def get_next_token(token_tuple, line_number):
    global active_row, symbol_row, no_bracket_function, scope, gl_line_number, func_in_call, count_params, parameter_counted, call_params, func_declare_started, function_row, func_call_table_list
    gl_line_number = line_number
    next_token = False
    if token_tuple != "$":
        print(f"[DEBUG] Processing token: {token_tuple} at line {line_number}")
        print(f"[DEBUG] DFA.states_stack (before any processing): {list(DFA.states_stack)}")
        if token_tuple[1] == "{":
            brackets.append(no_bracket_function)
            print(f"[DEBUG] Bracket '{{' encountered. Brackets stack: {brackets}")
            if no_bracket_function:
                # scope += 1
                no_bracket_function = False
        if token_tuple[1] == "}":
            bracket = brackets.pop()
            print(f"[DEBUG] Bracket '}}' encountered. Brackets stack: {brackets}")
            if bracket:
                symbol_table.check_void_var()
                symbol_table.remove_scope(scope)
                print(f"[DEBUG] Scope removed. Current scope: {scope}")
                scope -= 1
        # check for type missmatch error
        if token_tuple[0] == 'ID':
            id_row = symbol_table.get_row(token_tuple[1])
            if id_row is not None and id_row.is_arr and id_row.category == "var"\
                    and not func_declare_started and not active_row:
                arrays_stack.append(id_row)
                print(f"[DEBUG] Array ID pushed to arrays_stack: {id_row}")
        if token_tuple[1] == ']':
            if arrays_stack.__len__() > 0:
                popped = arrays_stack.pop()
                print(f"[DEBUG] Array ID popped from arrays_stack: {popped}")
        if token_tuple[1] == ';' or token_tuple[1] == ')':
            if arrays_stack.__len__() > 0:
                print(f"[DEBUG] Type mismatch error: array used as int. arrays_stack: {arrays_stack}")
                error(SymbolTable.ErrorTypeEnum.type_mismatch, arrays_stack[0].lexeme,
                                                   illegal="array", expected="int")
                arrays_stack.pop()
    while not next_token:
        print(f"[DEBUG] DFA.states_stack (top of loop): {list(DFA.states_stack)}")
        if not DFA.states_stack:
            print(f"[DEBUG] Stack underflow! Current token: {token_tuple}, line: {line_number}")
            raise RuntimeError("Parser stack underflow: DFA.states_stack is empty. Check your grammar and parser logic.")
        last_state_id = DFA.states_stack[DFA.states_stack.__len__() - 1]
        print(f"[DEBUG] last_state_id: {last_state_id}")
        last_state = DFA.id_state_dict[last_state_id]
        print(f"[DEBUG] last_state: {last_state}")
        print(f"[DEBUG] Current token: {token_tuple}")
        print(f"[DEBUG] Current stack: {list(DFA.states_stack)}")
        print(f"[DEBUG] Current state object: {last_state}")
        if hasattr(last_state, 'nterminal_id'):
            print(f"[DEBUG] Current nonterminal: {getattr(last_state, 'nterminal_id', None)}")
        if token_tuple == '$':
            print(f"[DEBUG] End of input reached. Calling next_state with '$'.")
            next_token, e = last_state.next_state(
                '$', '$', line_counter, semantic)
            print(f"[DEBUG] next_state returned: {next_token}, error: {e}")
        else:
            # error-check
            # function parameter number error check
            if token_tuple[0] == 'ID' and last_state.terminal_trans.keys().__contains__("#pid") and token_tuple[
                1] != "output":
                row = symbol_table.get_row(token_tuple[1])
                if row is not None and row.category == "func":
                    fcb = SymbolTable.FuncCallBlock(row)
                    func_call_table_list.append(fcb)
                    print(f"[DEBUG] Function call block pushed: {fcb}")
            elif token_tuple[0] == 'ID' and func_call_table_list.__len__() > 0 and token_tuple[1] != "output":
                param_row: SymbolTable.SymbolRow
                param_row = symbol_table.get_row(token_tuple[1])
                if func_call_table_list[-1].start_param:
                    if param_row in arrays_stack:
                        arrays_stack.remove(param_row)
                    func_call_table_list[func_call_table_list.__len__() - 1].add_param_row(param_row)
                    print(f"[DEBUG] Param row added to function call: {param_row}")
            elif token_tuple[0] == 'NUM' and func_call_table_list.__len__() > 0 and token_tuple[1] != "output":
                param_row = SymbolTable.SymbolRow()
                param_row.args_cells = 0
                param_row.lexeme = str(token_tuple[1])
                param_row.category = "var"
                param_row.type = "int"
                func_call_table_list[func_call_table_list.__len__() - 1].add_param_row(param_row)
                print(f"[DEBUG] NUM param row added to function call: {param_row}")
            if token_tuple[1] == ',' and func_call_table_list.__len__() > 0:
                func_call_table_list[func_call_table_list.__len__() - 1].next_param()
                print(f"[DEBUG] Function call next_param triggered.")
            if token_tuple[1] == '(' and func_call_table_list.__len__() > 0:
                func_call_table_list[func_call_table_list.__len__() - 1].start_param = True
                print(f"[DEBUG] Function call start_param set to True.")
            if token_tuple[1] == ')' \
                    and last_state.nterminal_id == "Arg-list-prime" and func_call_table_list.__len__() > 0:
                # finish func call
                # check for errors
                func_call_table = func_call_table_list.pop()
                print(f"[DEBUG] Function call block popped: {func_call_table}")
                if func_call_table.call_params.__len__() == func_call_table.function_row.params_type.__len__():
                    for i in range(func_call_table.call_params.__len__()):
                        if func_call_table.call_params[i].is_arr != func_call_table.function_row.params_type[i].is_arr:
                            expected = "array" if func_call_table.function_row.params_type[i].is_arr else "int"
                            illegal = "array" if func_call_table.call_params[i].is_arr else "int"
                            print(f"[DEBUG] Type matching error in function call: expected {expected}, got {illegal}")
                            error(SymbolTable.ErrorTypeEnum.type_matching,
                                                               func_call_table.function_row.lexeme, illegal=illegal,
                                                               arg=i + 1,
                                                               expected=expected)
                else:
                    print(f"[DEBUG] Number matching error in function call.")
                    error(SymbolTable.ErrorTypeEnum.number_mathing,
                                                           func_call_table.function_row.lexeme, )

            # pars table
            if token_tuple[0] == 'KEYWORD' and (token_tuple[1] == "int" or token_tuple[1] == "void"):
                if last_state.nterminal_id == "Params" and token_tuple[1] == "void":
                    # void in function input
                    print(f"[DEBUG] Void in function input.")
                    pass
                else:
                    symbol_row.type = token_tuple[1]
                    active_row = True
                    print(f"[DEBUG] Active row set: {symbol_row}")
                    if last_state.nterminal_id == "Type-specifier":
                        if symbol_row.category != "param":
                            symbol_row.category = "var"
                            print(f"[DEBUG] Symbol row category set to var.")
                    elif last_state.nterminal_id == "Params" or func_declare_started:
                        func_declare_started = True
                        if symbol_row.category != "param":
                            symbol_row.category = "param"
                            symbol_table.inc_func_args(symbol_row)
                            print(f"[DEBUG] Symbol row category set to param and inc_func_args called.")

            if last_state.nterminal_id == "Fun-declaration-prime":
                no_bracket_function = True
                func_declare_started = False
                symbol_table.set_line_category(line_number, "func")
                scope += 1
                print(f"[DEBUG] Fun-declaration-prime: scope incremented to {scope}")

            if token_tuple[0] == 'ID' and active_row:
                symbol_row.lexeme = token_tuple[1]
                symbol_row.line = line_number
                symbol_row.scope = scope
                symbol_table.add(symbol_row)
                print(f"[DEBUG] Symbol row added: {symbol_row}")
                symbol_row = SymbolTable.SymbolRow()
                active_row = False
            if token_tuple[0] == 'NUM' and last_state.nterminal_id == "Var-declaration-prime":
                symbol_table.set_last_args(int(token_tuple[1]),
                                           TempManager.get_instance().get_arr_temp(int(token_tuple[1])))
                print(f"[DEBUG] set_last_args called for array size: {token_tuple[1]}")
            if token_tuple[1] == ';':
                symbol_table.check_void_var()
                print(f"[DEBUG] check_void_var called after ';'")
            if token_tuple[1] == ']' and func_declare_started:
                symbol_table.set_last_args(0, 0)
                print(f"[DEBUG] set_last_args called for array close.")
            if token_tuple[1] == ')':
                func_declare_started = False
                print(f"[DEBUG] func_declare_started set to False after ')'")

            if token_tuple[0] == 'KEYWORD' or token_tuple[0] == 'SYMBOL':
                token = token_tuple[1]
            else:
                token = token_tuple[0]
            if token_tuple[1] == "output":
                token = "output"
            print(f"[DEBUG] Calling next_state with token: {token}, token_tuple: {token_tuple}, line: {line_number}")
            next_token, e = last_state.next_state(
                token, token_tuple, line_number, semantic)
            print(f"[DEBUG] next_state returned: {next_token}, error: {e}")
        print(f"[DEBUG] DFA.states_stack (after next_state): {list(DFA.states_stack)}")
        if e is not None:
            print(f"[DEBUG] Error encountered: {e} | Token: {token_tuple} | State: {last_state_id} | Stack: {list(DFA.states_stack)}")
            errors.append(e)


def draw_tree():
    # print(pars_table.pars_table)

    x = semantic_errors
    if develop_mode:
        print("semantic errors: ")
        print(x)
    # pp_list_of_tuples(program_block)

    a = ""
    for pre, fill, node in DFA.RenderTree(DFA.first_node):
        p = ("%s%s" % (pre, node.name))
        x = "'"
        p = p.replace(x, "")
        a += p + "\n"
    return a[0:a.__len__() - 1]


def get_pars_errors():
    return errors
