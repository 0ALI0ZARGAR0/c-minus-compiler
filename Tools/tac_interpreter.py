from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

TAC_LINE_RE = re.compile(r"^\s*\d+\s*\t\s*\(([^,\s]+)?\s*,\s*([^,]*)\s*,\s*([^,]*)\s*,\s*([^)]*)\)\s*$")


def _parse_operand(op: str) -> Tuple[str, Optional[int]]:
    op = op.strip()
    if op == "" or op == ")":
        return ("empty", None)
    if op.startswith("#"):
        return ("imm", int(op[1:]))
    if op.startswith("@"):
        return ("ind", int(op[1:]))
    # direct address (may be int)
    return ("dir", int(op))


def _value_of(mem: Dict[int, int], kind: str, val: Optional[int]) -> int:
    if kind == "imm":
        assert val is not None
        return val
    if kind == "dir":
        assert val is not None
        return mem.get(val, 0)
    if kind == "ind":
        assert val is not None
        # Indirect: memory[value at address]
        ptr = mem.get(val, 0)
        return mem.get(ptr, 0)
    return 0


def _assign(mem: Dict[int, int], dst_kind: str, dst: Optional[int], value: int) -> None:
    if dst_kind == "dir":
        assert dst is not None
        mem[dst] = value
        return
    if dst_kind == "ind":
        assert dst is not None
        ptr = mem.get(dst, 0)
        mem[ptr] = value
        return
    # empty or imm are invalid destinations; ignore


def load_tac(path: str) -> List[Tuple[str, Tuple[str, Optional[int]], Tuple[str, Optional[int]], Tuple[str, Optional[int]]]]:
    program: List[Tuple[str, Tuple[str, Optional[int]], Tuple[str, Optional[int]], Tuple[str, Optional[int]]]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = TAC_LINE_RE.match(line)
            if not m:
                # allow placeholder empty PB lines
                if "( , , , )" in line:
                    program.append(("NOP", ("empty", None), ("empty", None), ("empty", None)))
                    continue
                # ignore unparseable line
                continue
            op = (m.group(1) or "").strip()
            a1 = _parse_operand(m.group(2))
            a2 = _parse_operand(m.group(3))
            a3 = _parse_operand(m.group(4))
            program.append((op, a1, a2, a3))
    return program


def run_tac(path: str) -> List[int]:
    mem: Dict[int, int] = {}
    code = load_tac(path)
    outputs: List[int] = []
    pc = 0
    n = len(code)
    while 0 <= pc < n:
        op, a1, a2, a3 = code[pc]
        if op in ("", "NOP"):
            pc += 1
            continue
        if op == "ASSIGN":
            val = _value_of(mem, *a1)
            _assign(mem, *a2, val)
            pc += 1
        elif op == "ADD":
            v1 = _value_of(mem, *a1)
            v2 = _value_of(mem, *a2)
            _assign(mem, *a3, v1 + v2)
            pc += 1
        elif op == "SUB":
            v1 = _value_of(mem, *a1)
            v2 = _value_of(mem, *a2)
            _assign(mem, *a3, v1 - v2)
            pc += 1
        elif op == "MULT":
            v1 = _value_of(mem, *a1)
            v2 = _value_of(mem, *a2)
            _assign(mem, *a3, v1 * v2)
            pc += 1
        elif op == "EQ":
            v1 = _value_of(mem, *a1)
            v2 = _value_of(mem, *a2)
            _assign(mem, *a3, 1 if v1 == v2 else 0)
            pc += 1
        elif op == "LT":
            v1 = _value_of(mem, *a1)
            v2 = _value_of(mem, *a2)
            _assign(mem, *a3, 1 if v1 < v2 else 0)
            pc += 1
        elif op == "JP":
            # target must be direct value in a1
            kind, val = a1
            if kind == "dir" and val is not None:
                pc = val
            elif kind == "imm" and val is not None:
                pc = val
            else:
                # Unsupported target addressing, stop
                break
        elif op == "JPF":
            cond = _value_of(mem, *a1)
            kind, val = a2
            if cond == 0:
                if kind in ("dir", "imm") and val is not None:
                    pc = val
                else:
                    break
            else:
                pc += 1
        elif op == "PRINT":
            val = _value_of(mem, *a1)
            outputs.append(val)
            pc += 1
        else:
            # Unknown op: skip
            pc += 1
    return outputs


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 tac_interpreter.py <tac_file>")
        sys.exit(1)
    
    outputs = run_tac(sys.argv[1])
    for output in outputs:
        print(f"PRINT    {output}")


