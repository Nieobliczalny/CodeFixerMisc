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
        bugs = self.ccdb.getAllBugsForChecker('clang-diagnostic-constant-conversion')
        lines = []
        linesSingle = {}
        linesToSuppress = []
        for bug in bugs:
            if bug[2] == fileData[-1][0]:
                self.bugData = self.ccdb.getBugData(bug[0])
                if self.bugData.getLine() in linesSingle:
                    linesSingle[self.bugData.getLine()] += 1
                else:
                    linesSingle[self.bugData.getLine()] = 1
        for k in linesSingle:
            if linesSingle[k] > 5:
                linesToSuppress.append(k)
        inserts = 0
        for bug in bugs:
            if bug[2] == fileData[-1][0]:
                self.bugData = self.ccdb.getBugData(bug[0])
                if self.bugData.getLine() not in lines:
                    self.loadCodeFromFile()

                    if self.bugData.getLine() not in linesToSuppress:
                        tokens = self.checkers.extractTokensForChecker('clang-diagnostic-constant-conversion', self.bugData.getMessage())
                        test = tokens
                        line = self.code[self.bugData.getLine() - 1 + inserts]
                        newLine = line.replace(tokens[0]['value'], '({0}){1}'.format(tokens[1]['value'], tokens[0]['value']))
                        if line == newLine:
                            tokens[0]['value'] = self.findMatchingDefine(tokens[0]['value'])
                            if tokens[0]['value'] is not None:
                                newLine = line.replace(tokens[0]['value'], '({0}){1}'.format(tokens[1]['value'], tokens[0]['value']))
                        if line == newLine:
                            s = re.search('= (.*);', line)
                            expr = s.group(1)
                            newLine = line.replace(expr, '({0})({1})'.format(tokens[1]['value'], expr))
                        self.code[self.bugData.getLine() - 1 + inserts] = newLine
                    else:
                        line = self.code[self.bugData.getLine() - 1 + inserts]
                        self.code[self.bugData.getLine() - 1 + inserts] = '// codechecker_intentional [clang-diagnostic-constant-conversion] Suppress\n{0}'.format(line)
                        inserts += 1

                    self.saveCodeToFile()
                    lines = lines + list(range((self.bugData.getLine() - 11), (self.bugData.getLine() + 10)))
                    
                    print("Passed, suppressed: {0}".format(self.bugData.getLine() in linesToSuppress))
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