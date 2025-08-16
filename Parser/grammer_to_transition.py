from Parser import DFA

nterminal_id_dict = dict()
last_nterminal = ""
# State = DFA.State
# line = (f.readline())


def fill_nterminal_id_dict(grammar):
    i = 0
    for line in grammar.splitlines():
        if not line.strip() or '->' not in line:
            continue
        nterminal = line.split('->')[0].strip()
        nterminal_id_dict[nterminal] = i
        i += 1


def is_terminal(element):
    global last_nterminal
    if nterminal_id_dict.__contains__(element):
        last_nterminal = element
        return nterminal_id_dict[element]
    return -1


state_id_index = 0


def print_first_follow_sets():
    print("[DFA DEBUG] FIRST and FOLLOW sets:")
    for nt in DFA.nterminal_first_dict:
        print(f"[DFA DEBUG] FIRST({nt}): {DFA.nterminal_first_dict[nt]}")
    for nt in DFA.nterminal_follow_dict:
        print(f"[DFA DEBUG] FOLLOW({nt}): {DFA.nterminal_follow_dict[nt]}")

# Call this at the start of DFA construction
print_first_follow_sets()


def rule_to_states(State, line):
    global state_id_index
    # Skip empty or malformed lines
    if '->' not in line:
        return
    rule_list = line.split("->")
    if len(rule_list) < 2:
        return
    main_nterminal = rule_list[0].strip()
    first_state_id = state_id_index + 1
    state_id_index += 1
    DFA.nterminal_first_state[main_nterminal] = first_state_id
    final_state_id = state_id_index + 1
    state_id_index += 1
    State(final_state_id, 0, dict(), {}, True)
    first_state_terminal_trans = dict()
    first_state_nterminal_trans = set()
    righties = rule_list[1].split("|")
    for righty in righties:
        righty_list = [tok if tok != 'epsilon' else '' for tok in righty.split()]
        if not righty_list or righty_list == ['']:
            # Epsilon production: direct transition to final state
            print(f"[DFA DEBUG] Epsilon production for {main_nterminal}: {first_state_id} -> {final_state_id}")
            State(
                first_state_id,
                main_nterminal,
                first_state_terminal_trans,
                first_state_nterminal_trans,
                False,
            )
            continue
        for i in range(len(righty_list)):
            symbol = righty_list[i]
            if symbol == "EPSILON":
                symbol = ""
            if i == 0:
                state_id = first_state_id
            else:
                state_id = state_id_index + 1
                state_id_index += 1
            if i == len(righty_list) - 1:
                next_state_id = final_state_id
            else:
                next_state_id = state_id_index + 1
            state_terminal_trans = dict()
            state_nterminal_trans = set()
            if i == 0:
                state_terminal_trans = first_state_terminal_trans
                state_nterminal_trans = first_state_nterminal_trans
            # Always check if symbol is a nonterminal
            if symbol in DFA.nterminal_first_dict:
                # Nonterminal: add transitions for all tokens in its FIRST set (except epsilon)
                for t in DFA.nterminal_first_dict[symbol]:
                    if t != '':
                        state_terminal_trans[t] = next_state_id
                        print(f"[DFA DEBUG] State {state_id} ({main_nterminal}) terminal transition (from FIRST set): '{t}' -> {next_state_id}")
                state_nterminal_trans.add((symbol, next_state_id))
                print(f"[DFA DEBUG] State {state_id} ({main_nterminal}) nonterminal transition: '{symbol}' -> {next_state_id}")
            else:
                # Terminal: add transition for the terminal itself
                state_terminal_trans[symbol] = next_state_id
                print(f"[DFA DEBUG] State {state_id} ({main_nterminal}) terminal transition: '{symbol}' -> {next_state_id}")
            if i != 0:
                State(
                    state_id,
                    last_nterminal,
                    state_terminal_trans,
                    state_nterminal_trans,
                    False,
                )
    State(
        first_state_id,
        main_nterminal,
        first_state_terminal_trans,
        first_state_nterminal_trans,
        False,
    )
    print(f"[DFA DEBUG] State {first_state_id} ({main_nterminal}) created with terminals: {first_state_terminal_trans} and nonterminals: {first_state_nterminal_trans}")
