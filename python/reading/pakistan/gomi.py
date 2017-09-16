# coding = utf-8

with open("newdata.csv", "w", encoding="utf-8") as output:
    with open("data.csv", "r", encoding="utf-8") as f:
        output.write(f.readline())
        count = 0
        temp = ""
        while True:
            count += 1
            line = f.readline()
            if line == "":
                break
            if line.split(",")[0].isdigit() == False or int(line.split(",")[0]) != count:
                temp = temp[:-1] + line
                count -= 1
            else:
                if temp != "":
                    output.write(temp)
                temp = line
