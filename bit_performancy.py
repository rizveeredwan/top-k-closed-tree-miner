import random
# Python program to show time by process_time()
from time import process_time


def calculate_pow_2(_range):
    curr_value = 1
    _dict = {1: 0}
    arr = []
    for i in range(1, _range+1):
        curr_value = curr_value * 2
        # arr.append(curr_value)
        _dict[curr_value] = i
    return arr, _dict


def set_bit_positions(number, _range, set_bit_count, arr):
    while set_bit_count > 0:
        position = random.randint(0, _range)
        if number & (1 << position) == 0:
            number = number | (1 << position)
            set_bit_count -= 1
    return number


def finding_positions_using_divide(number):
    st = process_time()
    cnt = -1
    save = []
    while number > 0:
        cnt +=1
        rem = number % 2
        if rem == 1:
            save.append(cnt)
        number //= 2
    en = process_time()
    print(len(save), save[0:20])
    print("time = ", en-st)
    return


def finding_positions_using_bits(number, _dict):
    st = process_time()
    save = []
    while number > 0:
        value = number & (-number)
        save.append(_dict[value])
        number = number ^ value
    en = process_time()
    print(len(save), save[0:20])
    print("time = ", en - st)
    return

arr = []
arr, _dict = calculate_pow_2(_range=100000)
st = process_time()
number = set_bit_positions(0, 100000, 500, arr)
print(number)
en = process_time()
print(en-st)

# using normal solution
finding_positions_using_divide(number)

# using bit based solution
finding_positions_using_bits(number, _dict)


