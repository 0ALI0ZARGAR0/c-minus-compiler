import re
from dataclasses import dataclass


@dataclass
class RE:
    MY_DIGIT = re.compile(r"[0-9]")
    MY_LETTER = re.compile(r"[a-zA-Z]")
    MY_LETDIG = re.compile(r"[a-zA-Z0-9]")
    MY_SYMB = re.compile(r"[\[\]\(\)\{\}\;\:\-\+\<\,]")
    KEYWORDS = re.compile(
        r"^if$|^else$|^void$|^int$|^repeat$|^break$|^until$|^while$|^return$|^endif$"
    )
    MY_WHITESPACE = re.compile(r" |\t|\n|\r|\v|\f")
    MY_FORSLASH = re.compile(r"\/")
    MY_STAR = re.compile(r"\*")
    MY_EQ = re.compile(r"\=")
    MY_NEWLINE = re.compile(r"\n")
    MY_ALPHABET = re.compile(
        r"[a-zA-Z0-9]|[\[\]\(\)\{\}\;\:\-\+\<\,\=\/\*]|[\s|\t|\n|\r|\v|\f]"
    )
