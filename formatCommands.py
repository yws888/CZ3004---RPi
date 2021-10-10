

cmds = ['A90','W15', 'D90', 'D90', 'W50','D90', 'D90', 'A90']
parsed = []

if __name__ == '__main__':
    for cmd in cmds:
        parsed.append({"command": 'move', "direction": cmd})

    print(parsed)
