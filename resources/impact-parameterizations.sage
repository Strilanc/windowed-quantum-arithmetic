# @Craig: These are rather naïve extrapolations; can this be improved?

def ln(x): # The natural logarithm.
    return log(x) / log(e);

def log2(x): # The base 2 logarithm.
    return log(x) / log(2);


def runtime(n, n_e):
    return 2750 * n * n_e + 0.6 * n * n_e * log2(n);

def logical_qubits(n, n_e, g2 = 1024):
    return 3 * n + 2500 * ceil(n / g2);

def scaled_runtime(n, n_e): # in hours
    return 7 * float(runtime(n, n_e) / runtime(2048, 3029));

def scaled_logical_qubits(n, n_e): # in millions
    return 23 * float(logical_qubits(n, n_e) / logical_qubits(2048, 3029));

def scaled_volume(n, n_e): # in millions
    return scaled_runtime(n, n_e) * scaled_logical_qubits(n, n_e) / 24;


def fips_strength_level(n):
    # From FIPS 140-2 IG CMVP, page 110.
    #
    # This is extrapolated from the asymptotic complexity of the sieving
    # step in the general number field sieve (GNFS).

    return (1.923 * (n * ln(2))^(1/3) * ln(n * ln(2))^(2/3) - 4.69) / ln(2);

def fips_strength_level_rounded(n): # NIST-style rounding
    return 8 * round(fips_strength_level(n) / 8);


# Moduli lengths.
moduli = [1024, 1536, 2048, 3072, 4096, 6144, 8192, 15360, 16384];

# Pre-computed tuples on the form [modulus length, classical security level].
table = [[n, fips_strength_level_rounded(n)] for n in moduli];


# The delta parameter for solving RSA IFP via the short DLP in a single run.
delta = 20;


def print_rsa():
    print ""
    print "RSA:";

    for [n, _] in table:
        m = n/2 - 1;
        l = m - delta;
        n_e = m + 2 * l;

        print "n =", n, " n_e =", n_e, " m =", m, " l =", l, \
            " runtime =", scaled_runtime(n, n_e), \
            " logical qubits =", scaled_logical_qubits(n, n_e), \
            " volume =", scaled_volume(n, n_e);


def print_dlog_schnorr():
    print ""
    print "Schnorr groups:";

    for [n, z] in table:
        m = 2 * z;
        n_e = 2 * m;

        print "n =", n, " n_e =", n_e, " m =", m, \
            " runtime =", scaled_runtime(n, n_e), \
            " logical qubits =", scaled_logical_qubits(n, n_e), \
            " volume =", scaled_volume(n, n_e);

def print_dlog_safe_prime_short_length():
    print ""
    print "Safe-prime groups, short exponents:";

    for [n, z] in table:
        m = 2 * z;
        l = m;
        n_e = m + 2 * l;

        print "n =", n, " n_e =", n_e, " m =", m, " l =", l, \
            " runtime =", scaled_runtime(n, n_e), \
            " logical qubits =", scaled_logical_qubits(n, n_e), \
            " volume =", scaled_volume(n, n_e);

def print_dlog_safe_prime_full_length():
    print ""
    print "Safe-prime groups, full length exponents:";

    for [n, z] in table:
        m = n - 1; # N = 2r + 1 where r is prime, m is the bit length of r
        n_e = 2 * m;

        print "n =", n, " n_e =", n_e, " m =", m, \
            " runtime =", scaled_runtime(n, n_e), \
            " logical qubits =", scaled_logical_qubits(n, n_e), \
            " volume =", scaled_volume(n, n_e)

def print_dlog():
    print ""
    print "Discrete logarithms:";

    print_dlog_schnorr();
    print_dlog_safe_prime_short_length();
    print_dlog_safe_prime_full_length();


def print_all():
    print_rsa();
    print_dlog();


print_all();
