from ccdatabase import CCDatabase
from codechecker import CodeChecker
from config import config
from checkers import Checkers
import entities
import sys
import re

class FixTautOORCmp():
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
    
    def findMatchingDefine(self, value):
        patValue = '({0})'
        patName = '[ \t]([0-9a-zA-Z_]+)[ \t]'
        for line in self.code:
            if line[:7] == '#define':
                if re.search(patValue.format(value), line):
                    return re.search(patName, line).group(1)
        return None
    
    def fix(self, file):
        fileData = self.ccdb.getFileData(file)
        print(fileData)
        bugs = self.ccdb.getAllBugsForChecker('clang-diagnostic-tautological-constant-out-of-range-compare')
        lines = []
        for bug in bugs:
            if bug[2] == fileData[-1][0]:
                self.bugData = self.ccdb.getBugData(bug[0])
                if self.bugData.getLine() not in lines:
                    self.loadCodeFromFile()

                    tokens = self.checkers.extractTokensForChecker('clang-diagnostic-tautological-constant-out-of-range-compare', self.bugData.getMessage())
                    line = self.code[self.bugData.getLine() - 1]
                    pat = "\([^\(]*{0}\)".format(tokens[0]['value'])
                    match = re.search(pat, line)
                    if match is None:
                        pat = "\([^\(]*{0}\)".format(self.findMatchingDefine(tokens[0]['value']))
                        match = re.search(pat, line)
                    match = match.group(0)
                    newLine = line.replace(match, '({0})'.format(tokens[1]['value']))
                    self.code[self.bugData.getLine() - 1] = newLine

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
    fixer = FixTautOORCmp()
    fixer.fix(file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing file argument")
    else:
        main(sys.argv[1])