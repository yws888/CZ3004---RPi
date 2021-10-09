

cmds = ['W10', 'D17', 'W70', 'A6', 'W20', 'A11', 'W10', 'S40', 'C11', 'S10', 'A6', 'Z6', 'D6', 'Z6', 'D6', 'A6', 'W10', 'A17', 'C11', 'W30', 'A6', 'W50', 'D11', 'W10', 'D6', 'W10', 'D11', 'Z11', 'D6', 'W60', 'A6', 'W10', 'A6', 'W10', 'A17']

parsed = []

if __name__ == '__main__':
    for cmd in cmds:
        parsed.append({"command": 'move', "direction": cmd})

    print(parsed)
