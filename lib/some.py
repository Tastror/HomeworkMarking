import os

class Some:
    def __init__(self, path: str):
        self.path = path
        self.result = dict()

    def read(self) -> dict:
        self.result = dict()
        if not os.path.exists(self.path):
            return dict()
        with open(self.path, 'r') as f:
            first_line = True
            now_line = ""
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line == "":
                    first_line = True
                    continue
                elif first_line:
                    first_line = False
                    now_line = line
                    self.result.setdefault(now_line, [])
                else:
                    self.result[now_line].append(line)
        return self.result

    def add(self, name, value):
        if name not in self.result:
            self.result[name] = []
        self.result[name].append(value)

    def dump(self):
        start = True
        with open(self.path, 'w') as f:
            for key, value in self.result.items():
                if start:
                    start = False
                    f.write(f"{key}\n")
                else:
                    f.write(f"\n{key}\n")
                for line in value:
                    f.write(f"{line}\n")

if __name__ == '__main__':
    some = Some('some')
    result = some.read()
    print(result)
    some.add('new_key', 'new_value')
    some.dump()
