def map_number(number):
    number_mapper = {
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '۰': '0',
    }
    return ''.join(number_mapper.get(char, char) for char in number)



print(map_number("۴۴۵۶۴"))
