

cmds = ['A90','D180', 'W60', 'D180', 'A90']
parsed = []

if __name__ == '__main__':
    for cmd in cmds:
        parsed.append({"command": 'move', "direction": cmd})

    print(parsed)
