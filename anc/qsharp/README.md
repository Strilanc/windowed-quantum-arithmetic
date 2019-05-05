# Q# cost estimates for windowed arithmetic

To produce cost estimates, open this folder in Visual Studio Code and launch the project.
The results will be printed to the terminal in CSV format.
Due to overheads in the simulators, this will take several hours to finish.

Notes:

- Did not implement efficient uncomputation of table lookups, because the operations involved are not supported by Q#'s Toffoli simulator.
- The Karatsuba implementation was ported from https://github.com/Strilanc/quantum-karatsuba-2019, with slight tweaks to make it apply to the const*quantum case.
