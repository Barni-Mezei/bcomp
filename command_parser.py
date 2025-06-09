import sys

if len(sys.argv[1::]) == 0:
    print("No input file given!")
    exit()

if not ".csv" in sys.argv[1]:
    print("Invalid or missing file type! (Must be .csv)")
    exit()

print(f"--- Parsing '{sys.argv[1]}'")

out = open("commands.txt", "w", encoding="utf8")

with open(sys.argv[1], "r", encoding="utf8") as f:
    for i, line in enumerate(f):
        if i == 0: continue #Ignore first row

        line = line.strip().split(",")[8:12] #Get middle 4 rows

        if line[0] == "" or line[1] == "": continue #Skip if no command in line

        line[3] = "0" if line[3] == "-" or line[3] == "-" else "1" #Set argument requirement

        print(f"{i:02d}: {line}")
        out.write(line[1].lower() + " ")
        out.write(line[0] + " ")
        out.write(line[3] + " ")
        out.write("\n")

print("--- File saved as commands.txt")

out.close()