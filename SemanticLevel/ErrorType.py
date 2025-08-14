import enum

gl_line_number = 0

semantic_errors = []


class ErrorTypeEnum(enum.Enum):
    scoping = 1
    void_type = 2
    number_mathing = 3
    break_stmt = 4
    type_mismatch = 5
    type_matching = 6


def error(err_type, identifier, expected=None, illegal=None, arg=None):
    """Record a semantic error in the required textual format.

    Args:
        err_type: ErrorTypeEnum indicating the error category.
        identifier: The related identifier name (or function name).
        expected: Expected type/name when applicable.
        illegal: Actual, illegal, or mismatched type/name when applicable.
        arg: The argument index for argument-related errors.
    """
    line_number = str(gl_line_number)
    identifier = str(identifier)
    if err_type == ErrorTypeEnum.scoping:
        err = "#" + line_number + ": Semantic Error! '" + identifier + "' is not defined."
    elif err_type == ErrorTypeEnum.void_type:
        err = "#" + line_number + ": Semantic Error! Illegal type of void for '" + identifier + "'."
    elif err_type == ErrorTypeEnum.number_mathing:
        err = "#" + line_number + \
              ": Semantic Error! Mismatch in numbers of arguments of '" + identifier + "'."
    elif err_type == ErrorTypeEnum.break_stmt:
        err = "#" + line_number + \
              ": Semantic Error! No 'repeat ... until' found for 'break'."
    elif err_type == ErrorTypeEnum.type_mismatch:
        err = "#" + line_number + ": Semantic Error! Type mismatch in operands, Got " + \
              str(illegal) + " instead of " + str(expected) + "."
    elif err_type == ErrorTypeEnum.type_matching:
        err = "#" + line_number + ": Semantic Error! Mismatch in type of argument " + str(arg) + \
              " of '" + identifier + "'. Expected '" + str(expected) + \
              "' but got '" + str(illegal) + "' instead."
    else:
        # Fallback to a generic message to avoid silent failures
        err = "#" + line_number + ": Semantic Error!"
    semantic_errors.append(err)
