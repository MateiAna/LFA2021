import sys

class Automaton:
    Q = None
    S = None
    d = None
    F = None
    q0 = None
    def __init__(self, Q, S, d, F, q0):
        self.Q=Q
        self.S=S
        self.d=d
        self.F=F
        self.q0=q0
    def __str__(self):
        s = ""
        s += "States:\n"+str(self.Q)+"\n"
        s += "Sigma:\n"+str(self.S)+"\n"
        s += "Final States:\n"+str(self.F)+"\n"
        s += "Initial State:\n"+str(self.q0)+"\n"
        s += "Transitions:\n"
        for (src,let), dst in self.d.items():
            s += "\t('"+str(src)+"', '"+str(let)+"') -> "+str(dst)+"\n"
        return s
    def isDFA(self):
        for (_,let), dst in self.d.items():
            if let == "lambda":
                return False
            if len(dst) != 1:
                return False
        return True
    def hasLambdaTransitions(self):
        for (_,let), _ in self.d.items():
            if let == "lambda":
                return True
        return False
    def runDFA(self, q_crt, lett):
        if (q_crt, lett) in self.d:
            return next(iter(self.d[(q_crt, lett)]))
        return None
    def runNFA(self, qs_crt, lett):
        qs_next = set()
        for q in qs_crt:
            if (q, lett) in self.d:
                qs_next.add(q)
        return qs_next
    def runLambdaNFA(self, qs_crt, lett):
        qs_closure = qs_crt.copy()
        modified = True
        while modified:
            modified = False
            for q in qs_closure:
                if (q, "lambda") in self.d:
                    qs_closure.add(q)
                    modified = True
        if lett == "lambda":
            return qs_closure
        qs_next = set()
        for q in qs_closure:
            if (q, lett) in self.d:
                qs_next.add(q)
        modified = True
        while modified:
            modified = False
            for q in qs_next:
                if (q, "lambda") in self.d:
                    qs_next.add(q)
                    modified = True
        return qs_next

def checkWord(dfa, w):
    q_crt = dfa.q0
    for c in w:
        q_crt = dfa.runDFA(q_crt,c)
    return q_crt in dfa.F

def validateDFA(dfa, accept, reject, log=False):
    if accept != None:
        for w in accept:
            if not(checkWord(dfa,w)):
                print("should accept \""+w+"\"")
            elif log:
                print("correctly accepts \""+w+"\"")
    if reject != None:
        for w in reject:
            if checkWord(dfa,w):
                print("should reject \""+w+"\"")
            elif log:
                print("correctly rejects \""+w+"\"")

def isValidLetter(letter):
    return letter.find(' ') == -1
def isValidState(state):
    return state.find(' ') == -1

def read_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    return lines

def parse_lines(lines, strict = True, warn = True):
    state = "init"
    letters = None
    states = None
    finals = set()
    transitions = None
    required_states = dict()
    required_letters = dict()
    init = None
    errors = False
    accept = None
    reject = None
    for i,line in enumerate(lines):
        line = line.split('#')[0]
        if line == '':
            continue
        elif line.strip() == "Sigma:":
            if state != "init":
                if strict:
                    print("Error: Unexpected \"Sigma:\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Unexpected \"Sigma:\" at line: ", i+1,". Ending previous section.", sep = '')
            if letters == None:
                letters = set()
            else:
                if strict:
                    print("Error: Duplicate section \"Sigma:\" at line: ",i+1,sep='')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Duplicate section \"Sigma:\" at line: ",i+1,". Continuing previous",sep='')
            state = "Sigma"
        elif line.strip() == "Accept:" and not strict:
            if state != "init":
                if warn: print("Warning: Unexpected \"Accept:\" at line: ", i+1,". Ending previous section.", sep = '')
            if accept == None:
                accept = set()
            else:
                if warn: print("Warning: Duplicate section \"Accept:\" at line: ",i+1,". Continuing previous",sep='')
            state = "Accept"
        elif line.strip() == "Reject:" and not strict:
            if state != "init":
                if warn: print("Warning: Unexpected \"Reject:\" at line: ", i+1,". Ending previous section.", sep = '')
            if reject == None:
                reject = set()
            else:
                if warn: print("Warning: Duplicate section \"Reject:\" at line: ",i+1,". Continuing previous",sep='')
            state = "Reject"
        elif line.strip() == "States:":
            if state != "init":
                if strict:
                    print("Error: Unexpected \"States:\" at line : ", i+1, sep = '')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Unexpected \"States:\" at line : ", i+1,". Continuing previous", sep = '')
            if states == None:
                states = set()
            else:
                if strict:
                    print("Error: Duplicate section \"States:\" at line: ",i+1,sep='')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Duplicate section \"States:\" at line: ",i+1,". Continuing previous",sep='')
            state = "States"
        elif line.strip() == "Transitions:":
            if state != "init":
                if strict:
                    print("Error: Unexpected \"Transitions:\" at line : ", i+1, sep = '')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Unexpected \"Transitions:\" at line : ", i+1,". Continuing previous", sep = '')
            if transitions == None:
                transitions = dict()
            else:
                if strict:
                    print("Error: Duplicate section \"Transitions:\" at line: ",i+1,sep='')
                    errors =  True
                    continue
                else:
                    if warn: print("Warning: Duplicate section \"Transitions:\" at line: ",i+1,". Continuing previous",sep='')
            state = "Transitions"
        elif line.strip() == "End":
            if state == "init":
                print("Error: Unexpected \"End\" at line : ", i+1, sep = '')
                errors = True
                continue
            else:
                state = "init"
            
        else:
            if state == "Sigma":
                token = line.strip()
                if isValidLetter(token):
                    letters.add(token) 
                else:
                    print("Error: Invalid letter \"", token.strip(),"\" at line: ", i+1, sep = '')
                    errors = True
                    continue
            elif state == "Accept":
                token = line.strip()
                accept.add(token)
            elif state == "Reject":
                token = line.strip()
                reject.add(token) 
            elif state == "States":
                tokens = line.split(",")
                if len(tokens)>3 or len(tokens) == 0:
                    print("Error: Malformed state \"", line.strip(), "\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                token = tokens[0].strip()
                if isValidState(token):
                    states.add(token) 
                else:
                    print("Error: Invalid state \"",token.strip(),"\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                if len(tokens)==3 and tokens[1] == tokens[2]:
                    if strict:
                        print("Error: Repeated attribute \"",tokens[1].strip(),"\" at line: ", i+1, sep = '')
                        errors = True
                        continue
                for j in range(1,len(tokens)):
                    attr = tokens[j].strip()
                    if attr == "S":
                        if init == None:
                            init = token
                        else:
                            if strict:
                                print("Error: Duplicate initial state \"",token.strip(),"\" at line: ", i+1, sep = '')
                                errors = True
                                continue
                            else:
                                if warn: print("Warning: Duplicate initial state \"",token.strip(),"\" at line: ", i+1,". Replacing", sep = '')
                    elif attr == "F":
                        finals.add(token)
                    else:
                        print("Error: Invalid attribute \"",attr.strip(),"\" at line: ",i+1)
                        errors = True
                        continue
            elif state == "Transitions":
                tokens = line.split(",")
                if len(tokens)!=3:
                    if strict:
                        print("Error: Malformed transition \"", line.strip(), "\" at line: ", i+1, sep = '')
                        errors = True
                        continue
                    else:
                        if warn: print("Warning: Malformed transition \"", line.strip(), "\" at line: ", i+1,". Ignoring", sep = '')
                        continue
                if not isValidState(tokens[0].strip()):
                    print("Error: Invalid transition source state \"", tokens[0].strip(), "\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                if not isValidLetter(tokens[1].strip()):
                    print("Error: Invalid transition symbol/letter \"", tokens[1].strip(), "\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                if not isValidState(tokens[2].strip()):
                    print("Error: Invalid transition target state \"", tokens[2].strip(), "\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                key = (tokens[0].strip(),tokens[1].strip())
                if key in transitions:
                    transitions[key].add(tokens[2].strip())
                else:
                    transitions[key]=set([tokens[2].strip()])
                required_states[tokens[0].strip()]=i+1
                required_letters[tokens[1].strip()]=i+1
                required_states[tokens[2].strip()]=i+1
            else:
                if strict:
                    print("Error: Invalid token \"",line.strip(),"\" at line: ", i+1, sep = '')
                    errors = True
                    continue
                else:
                    if warn: print("Warning: Invalid token \"",line.strip(),"\" at line: ", i+1,". Treating as comment", sep = '')
                    
    if state != "init":
        if strict:
            print("Error: Unexpected end of file before end of section \"",state,"\"",sep='')
            errors = True
        else:
            if warn: print("Warning: Unexpected end of file before end of section \"",state,"\". Ignoring ",sep='')
            state = "init"

    if states == None:
        if strict:
            print("Error: Missing section \"States:\"" ,sep='')
            errors = True
        else:
            if warn: print("Warning: Missing section \"States:\". Adding as empty" ,sep='')
        states=set()
    if letters == None:
        if strict:
            print("Error: Missing section \"Sigma:\"" ,sep='')
            errors = True
        else:
            if warn: print("Warning: Missing section \"Sigma:\". Adding as empty" ,sep='')
        letters=set()
    if transitions == None:
        if strict:
            print("Error: Missing section \"Transitions:\"" ,sep='')
            errors = True
        else:
            if warn: print("Warning: Missing section \"Transitions:\". Adding as empty" ,sep='')
        transitions=dict()

    undefined_states = set(required_states.keys()).difference(states)
    undefined_letters = set(required_letters.keys()).difference(letters)
    for undefined_state in undefined_states:
        if strict:
            print("Error: Undefined state \"",undefined_state,"\" requied at line: ", required_states[undefined_state], sep="")
            errors = True
        else:
            if warn: print("Warning: Undefined state \"",undefined_state,"\" requied at line: ", required_states[undefined_state],". Adding to states", sep="")
            states.add(undefined_state)
    for undefined_letter in undefined_letters:
        if strict:
            print("Error: Undefined letter \"",undefined_letter,"\" requied at line: ", required_letters[undefined_letter], sep="")
            errors = True
        else:
            if warn: print("Warning: Undefined letter \"",undefined_letter,"\" requied at line: ", required_letters[undefined_letter],". Adding to sigma", sep="")
            letters.add(undefined_letter)
    if init == None:
        print("Error: Missing initial state")
        errors = True
    if len(finals) == None:
        if warn: print("Warning: No final state")
    if errors:
        return None
    else:
        a = Automaton(states,letters,transitions,finals,init)
        if a.isDFA() and (accept != None or reject != None):
            validateDFA(a,accept,reject,log=True)
        return a
    

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc > 1:
        lines = read_file(sys.argv[1])
    else:
        lines = read_file(input("Please enter the file: \n"))
    a = parse_lines(lines,strict=False,warn=False)
    if a:
        if a.isDFA() and argc > 2:
            if checkWord(a, sys.argv[2]):
                print("accept")
            else:
                print("reject")
        else:
            print("Your automaton is non-deterministic.")
    else:
        print("Invalid automaton")