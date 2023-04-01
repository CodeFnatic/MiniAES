# encoding: utf-8

from pyfinite import ffield
import time


def str_to_bin(str_char):
    '''
    :param str_char: string
    :return: listed binary form of string
    '''
    bin_str = "{:04b}".format(str_char)
    bin_arr = list(bin_str)
    new_array = []
    for element in bin_arr:
        new_array.append(int(element))
    return new_array


def arr_to_int(arr):
    '''
    :param arr: list to be modified
    :return: int value of list
    '''
    bit_array = []
    for element in arr:
        bit_array.append(str(element))
    new_array = ''.join(bit_array)
    int_val = int(new_array, 2)
    return int_val


def nibble_sub(nib):
    '''
    a0 a2                    b0 b2
    a1 a3 --> nibble_sub --> b1 b3
    '''
    sub_table = [[0b0000, 0b1110], [0b0001, 0b0100], [0b0010, 0b1101], [0b0011, 0b0001],
                 [0b0100, 0b0010], [0b0101, 0b1111], [0b0110, 0b1011], [0b0111, 0b1000],
                 [0b1000, 0b0011], [0b1001, 0b1010], [0b1010, 0b0110], [0b1011, 0b1100],
                 [0b1100, 0b0101], [0b1101, 0b1001], [0b1110, 0b0000], [0b1111, 0b0111]]
    for element in sub_table:
        if element[0] == nib:
            nib = element[1]
            break

    return nib


def nibble_sub_decrypt(nib):
    '''
    a0 a2                    b0 b2
    a1 a3 --> nibble_sub --> b1 b3
    '''
    sub_table = [[0b0000, 0b1110], [0b0001, 0b0011], [0b0010, 0b0100], [0b0011, 0b1000],
                 [0b0100, 0b0001], [0b0101, 0b1100], [0b0110, 0b1010], [0b0111, 0b1111],
                 [0b1000, 0b0111], [0b1001, 0b1101], [0b1010, 0b1001], [0b1011, 0b0110],
                 [0b1100, 0b1011], [0b1101, 0b0010], [0b1110, 0b0000], [0b1111, 0b0101]]
    for element in sub_table:
        if element[0] == nib:
            nib = element[1]
            break

    return nib


def shift_row(arr):
    '''
    Rotates each row of the input block to the left.
    b0 b2                   b0 b2   c0 c2
    b1 b3 --> shift_row --> b3 b1 = c1 c3
    '''
    temp = arr[1]
    arr[1] = arr[3]
    arr[3] = temp
    return arr


def key_addition(arr1, arr2):
    '''
    d0 d2     k0 k2   e0 e2
    d1 d3 xor k1 k3 = e1 e3
    '''
    if type(arr1) is not list:
        arr1 = str_to_bin(arr1)
    if type(arr2) is not list:
        arr2 = str_to_bin(arr2)
    e0 = arr1[0] ^ arr2[0]
    e1 = arr1[1] ^ arr2[1]
    e2 = arr1[2] ^ arr2[2]
    e3 = arr1[3] ^ arr2[3]
    arr = [e0, e1, e2, e3]
    return arr


def poly_multiply(val1, val2):
    '''
    :param val1: value to multiply (4bit)
    :param val2: value to multiply (4bit)
    :return: Galois Field multiplication result
    '''
    gf_1 = ffield.FField(4)             # create GF of 4
    result = gf_1.Multiply(val1, val2)  # multiply GFs
    result = str_to_bin(result)
    return result


def mix_column(arr):
    '''
    c0 c2                    d0 d2
    c1 c3 --> mix_column --> d1 d3
    d0   [3 2][c0]      d2    [3 2][c2]
    d1 = [2 3][c1]      d3 =  [2 3][c3]
    '''

    temp_1 = poly_multiply(0b0011, arr[0])
    temp_2 = poly_multiply(0b0010, arr[1])
    d0 = key_addition(temp_1, temp_2)
    d0 = arr_to_int(d0)
    temp_1 = poly_multiply(0b0010, arr[0])
    temp_2 = poly_multiply(0b0011, arr[1])
    d1 = key_addition(temp_1, temp_2)
    d1 = arr_to_int(d1)
    temp_1 = poly_multiply(0b0011, arr[2])
    temp_2 = poly_multiply(0b0010, arr[3])
    d2 = key_addition(temp_1, temp_2)
    d2 = arr_to_int(d2)
    temp_1 = poly_multiply(0b0010, arr[2])
    temp_2 = poly_multiply(0b0011, arr[3])
    d3 = key_addition(temp_1, temp_2)
    d3 = arr_to_int(d3)
    result = [d0, d1, d2, d3]
    return result


###################################################################
# Derivation of the Round Keys
###################################################################
'''
Generation of the Round Keys of Mini-AES
Round       Round Key Values
0               w0 = k0
                w1 = k1
                w2 = k2
                w3 = k3
1               w4 = w0 ⊕ NibbleSub( w3 ) ⊕ rcon(1)
                w5 = w1 ⊕ w4
                w6 = w2 ⊕ w5
                w7 = w3 ⊕ w6
2               w8 = w4 ⊕ NibbleSub( w7 ) ⊕ rcon(2)
                w9 = w5 ⊕ w8
                w10 = w6 ⊕ w9
                w11 = w7 ⊕ w10
'''


def round_key(key0, key1, key2, key3):
    '''
    Derivation of the Round Keys
    :param key0: key 0 nibble
    :param key1: key 1 nibble
    :param key2: key 2 nibble
    :param key3: key 3 nibble
    :return:
    '''
    w0 = key0
    w1 = key1
    w2 = key2
    w3 = key3
    w4_1 = nibble_sub(w3)
    w4 = key_addition(w0, w4_1)
    w4 = key_addition(w4, [0, 0, 0, 1])
    w4 = arr_to_int(w4)

    w5 = key_addition(w1, w4)
    w5 = arr_to_int(w5)
    w6 = key_addition(w2, w5)
    w6 = arr_to_int(w6)
    w7 = key_addition(w3, w6)
    w7 = arr_to_int(w7)

    w8_1 = nibble_sub(w7)
    w8 = key_addition(w4, w8_1)
    w8 = key_addition(w8, [0, 0, 1, 0])
    w8 = arr_to_int(w8)

    w9 = key_addition(w5, w8)
    w9 = arr_to_int(w9)
    w10 = key_addition(w6, w9)
    w10 = arr_to_int(w10)
    w11 = key_addition(w7, w10)
    w11 = arr_to_int(w11)
    k0 = key1
    k1 = key2
    k2 = key3
    k3 = key3
    K = [k0, k1, k2, k3]
    K0 = [w0, w1, w2, w3]
    K1 = [w4, w5, w6, w7]
    K2 = [w8, w9, w10, w11]
    return K, K0, K1, K2


###################################################################
# Encryption of the Plain Text
###################################################################
def encrypt(plain_text, key_0, key_1, key_2, key_3, print_flag=None):
    '''
    :param plain_text: text that will be encrypted
    :param key_0: key 0 to be encrypted with
    :param key_1: key 1 to be encrypted with
    :param key_2: key 2 to be encrypted with
    :param key_3: key 3 to be encrypted with
    :return: encrypted text
    '''
    print("Text to encode:    [{0}, {1}, {2}, {3}]".format(plain_text[0], plain_text[1], plain_text[2], plain_text[3]))
    K, K0, K1, K2 = round_key(key_0, key_1, key_2, key_3)
    P = plain_text
    enc_start = int(round(time.time() * 1000))
    # Round 1
    A = key_addition(P, K0)
    B = [nibble_sub(A[0]), nibble_sub(A[1]), nibble_sub(A[2]), nibble_sub(A[3])]
    C = shift_row(B)
    D = mix_column(C)
    E = key_addition(D, K1)
    # Round 2
    F = [nibble_sub(E[0]), nibble_sub(E[1]), nibble_sub(E[2]), nibble_sub(E[3])]
    G = shift_row(F)
    H = key_addition(G, K2)
    enc_end = int(round(time.time() * 1000))
    print("Final cipher text: " + str(H))
    print("Encryption time:   {0:.4f} ms\n".format((enc_end - enc_start)))
    if print_flag:
        print("Step by step encryption")
        print("A = {}".format(str(A)))
        print("B = {}".format(str(B)))
        print("C = {}".format(str(C)))
        print("D = {}".format(str(D)))
        print("E = {}".format(str(E)))
        print("F = {}".format(str(F)))
        print("G = {}".format(str(G)))
        print("H = {}\n".format(str(H)))
    return H


###################################################################
# Decryption of the Cipher Text
###################################################################
def decrypt(cipher_text, key_0, key_1, key_2, key_3, print_flag=None):
    '''
    :param cipher_text: Encoded text that will be decrypted
    :param key_0: decryption key 0
    :param key_1: decryption key 1
    :param key_2: decryption key 2
    :param key_3: decryption key 3
    :return: decrypted text
    '''
    print("Text to decode:    [{0}, {1}, {2}, {3}]".format(cipher_text[0], cipher_text[1], cipher_text[2], cipher_text[3]))
    K, K0, K1, K2 = round_key(key_0, key_1, key_2, key_3)
    dec_start = int(round(time.time() * 1000))
    # Round 1
    A = key_addition(cipher_text, K2)
    B = shift_row(A)
    C = [nibble_sub_decrypt(B[0]), nibble_sub_decrypt(B[1]), nibble_sub_decrypt(B[2]), nibble_sub_decrypt(B[3])]
    D = key_addition(C, K1)
    E = mix_column(D)
    # Round 2
    F = shift_row(E)
    G = [nibble_sub_decrypt(F[0]), nibble_sub_decrypt(F[1]), nibble_sub_decrypt(F[2]), nibble_sub_decrypt(F[3])]
    H = key_addition(G, K0)
    dec_end = int(round(time.time() * 1000))
    print("Decrypted text:    " + str(H))
    print("Decryption time:   {0:.4f} ms\n".format((dec_end - dec_start)))
    if print_flag:
        print("Step by step decryption")
        print("A = {}".format(str(A)))
        print("B = {}".format(str(B)))
        print("C = {}".format(str(C)))
        print("D = {}".format(str(D)))
        print("E = {}".format(str(E)))
        print("F = {}".format(str(F)))
        print("G = {}".format(str(G)))
        print("H = {}".format(str(H)))
    return H


###################################################################
# Main
###################################################################
print("           _       _         ___   _____ _____  ")
print("          (_)     (_)       / _ \ |  ___/  ___| ")
print(" _ __ ___  _ _ __  _ ______/ /_\ \| |__ \ `--.  ")
print("| '_ ` _ \| | '_ \| |______|  _  ||  __| `--. \ ")
print("| | | | | | | | | | |      | | | || |___/\__/ / ")
print("|_| |_| |_|_|_| |_|_|      \_| |_/\____/\____/  ")
print("By CodeFnatic\n")

# Plain text
p0 = 0b1001  # 9
p1 = 0b1100  # 12
p2 = 0b0110  # 6
p3 = 0b0011  # 3
P = [p0, p1, p2, p3]

# Cipher key (debug purposes)
k0 = 0b1100  # 12
k1 = 0b0011  # 3
k2 = 0b1111  # 15
k3 = 0b0000  # 0
cipher_text = encrypt(plain_text=P, key_0=k0, key_1=k1, key_2=k2, key_3=k3, print_flag=1)

# Cipher key (debug purposes)
k0 = 0b1100  # 12
k1 = 0b0011  # 3
k2 = 0b1111  # 15
k3 = 0b0000  # 0
decrypt(cipher_text=cipher_text, key_0=k0, key_1=k1, key_2=k2, key_3=k3, print_flag=1)


