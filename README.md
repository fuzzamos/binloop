# binloop
Find call graph loops in 64 bit binaries using objdump and some Python code

You can use this to find call graph loops in binaries.

For example, assume a C program with functions A() and B(). A() calls B() and B() calls A(). There's a loop.
If a sufficient depth is reached, the program will crash due to a stack overflow.
This is particulary problematic for server software; they might be prone to a remote crash if a very deep recursion is possible.
Hence, this tool can aid in the auditing of software, even if the source code is not known.
