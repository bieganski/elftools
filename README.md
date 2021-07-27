# elftools
find symbol, examine content of symbol etc

* `examine.sh`
find offset of given symbol and print it's content in hex

* `get_symbol.py`
given memory address it finds all possible symbols that address could belong too
(it may be many of them, as sometimes information about symbol sizes is missing).
