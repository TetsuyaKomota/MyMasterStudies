# coding = utf-8

with open("tmp/data.csv", "r", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if line == "":
            break
        if "32.9861" in line and "70.6042" in line:
            print(line)
