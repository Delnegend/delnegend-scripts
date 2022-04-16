def print_sign(text):
    top_bottom_bar = '=' * (len(text) + 8)
    space = '=' + ' ' * (len(text) + 6) + '='
    message = '=' + ' ' * 3 + text + ' ' * 3 + '='
    print(top_bottom_bar)
    print(space)
    print(message)
    print(space)
    print(top_bottom_bar)