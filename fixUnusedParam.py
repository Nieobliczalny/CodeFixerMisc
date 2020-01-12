from ccdatabase import CCDatabase
from codechecker import CodeChecker
from config import config
from checkers import Checkers
import entities
import sys
import re

class FixUnusedParam():
    def __init__(self):
        self.ccdb = CCDatabase(config.getCcDbFile())
        self.codeChecker = CodeChecker(config.getRepoDir())
        self.code = []
        self.checkers = Checkers()

    def loadCodeFromFile(self):
        with open(self.bugData.getFile(), 'r') as file:
            code = file.readlines()
            self.code = []
            for line in code:
                self.code.append(line.replace("\r\n", "\n"))
            """
            code = file.read()
            noCrLf = code.count("\r\n")
            noCr = code.count("\r") - noCrLf
            noLf = code.count("\n") - noCrLf
            if noCrLf > noCr:
                if noCrLf > noLf:
                    self.lineEnding = "\r\n"
                else:
                    self.lineEnding = "\n"
            else:
                if noCr > noLf:
                    self.lineEnding = "\r"
                else:
                    self.lineEnding = "\n"
            self.code = code.split(self.lineEnding)
            """

    def saveCodeToFile(self):
        with open(self.bugData.getFile(), 'w') as file:
           #file.write(self.lineEnding.join(self.code))
           file.writelines(self.code)
    
    def fix(self, file):
        fileData = self.ccdb.getFileData(file)
        print(fileData)
        bugs = self.ccdb.getAllBugsForChecker('clang-diagnostic-unused-parameter')
        lines = []
        inserts = 0
        for bug in bugs:
            if bug[2] == fileData[-1][0]:
                self.bugData = self.ccdb.getBugData(bug[0])
                if self.bugData.getLine() not in lines:
                    self.loadCodeFromFile()

                    newLine = '// codechecker_intentional [clang-diagnostic-unused-parameter] Suppress\n'
                    self.code.insert(self.bugData.getLine() - 1 + inserts, newLine)
                    inserts = inserts + 1

                    self.saveCodeToFile()
                    lines = lines + list(range((self.bugData.getLine() - 11), (self.bugData.getLine() + 10)))
                    print("Passed")
                    print(self.bugData.getLine())
                    pass
                else:
                    print("Dismissed")
                    print(self.bugData.getLine())
                    pass

def main(file):
    fixer = FixUnusedParam()
    fixer.fix(file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing file argument")
    else:
        main(sys.argv[1])