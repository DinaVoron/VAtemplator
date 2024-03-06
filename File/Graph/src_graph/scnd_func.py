def has_common_element(array1, array2):
    for element in array1:
        if element in array2:
            return True
    return False
