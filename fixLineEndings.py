import sys
import subprocess

def main(f):
    data = []
    with open(f, 'r') as file:
        code = file.readlines()
        for line in code:
            data.append(line.replace("\r\n", "\n"))
    with open(f, 'w') as file:
        file.writelines(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing file argument")
        for i in range(1,5001):
            #subprocess.call("python3 fixLineEndings.py ../TrainingData/main{0}.cpp".format(i), shell=True)
            subprocess.call("python3 fixDeadStore.py main{0}.cpp".format(i), shell=True)
            print(i)
    else:
        main(sys.argv[1])