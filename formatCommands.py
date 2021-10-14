

cmds = ['A50', 'W50', 'D118', 'W40','D118', 'W50','A50', 'D20']
parsed = []

if __name__ == '__main__':
    for cmd in cmds:
        parsed.append({"command": 'move', "direction": cmd})

    print(parsed)
