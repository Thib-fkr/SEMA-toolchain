SPECS = """
PLACE FUNCTION SPECIFICATION HERE
"""

def main():
    lines = SPECS.split('\n')
    lines = [l for l in lines if str.strip(l) != ""]
    assert '(' in lines[0]
    assert ')' in lines[-1]
    assert len(lines) >= 3

    print(lines[0].split(' ')[-1].split('(')[0])
    print(lines[0].split(' ')[0])
    print(" ".join([l.split()[-1].removeprefix('*') for l in lines[1:-1]]))

if __name__ == "__main__":
    main()
