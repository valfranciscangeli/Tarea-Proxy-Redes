"""  Modulo de funciones que trabajan con strings """
# ===============================================
def find_index_with_substring(substring, string_list):
    for index, string in enumerate(string_list):
        if substring in string:
            return index
    return -1

# ===============================================

def contains_end_of_head(message, end_sequence="\r\n\r\n"):
    return end_sequence in message
