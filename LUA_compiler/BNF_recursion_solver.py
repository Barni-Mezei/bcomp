class NonTerminal :
    def __init__(self, name) :
        self.name = name
        self.rules = []
    def addRule(self, rule) :
        self.rules.append(rule)
    def setRules(self, rules) :
        self.rules = rules
    def getName(self) :
        return self.name
    def getRules(self) :
        return self.rules
    def printRule(self) :
        print(self.name + " -> ", end = "")
        for i in range(len(self.rules)) :
            print(self.rules[i], end = "")
            if i != len(self.rules) - 1 :
                print(" | ", end = "")
        print()
        
        
class Grammar :
    def __init__(self) :
        self.nonTerminals = []

    def addRule(self, rule) :
        nt = False
        parse = ""

        for i in range(len(rule)) :
            c = rule[i]
            if c == ' ' :
                if not nt :
                    newNonTerminal = NonTerminal(parse)
                    self.nonTerminals.append(newNonTerminal)
                    nt = True
                    parse = ""
                elif parse != "" :
                    self.nonTerminals[len(self.nonTerminals) - 1].addRule(parse)
                    parse = ""
            elif c != '|' and c != '-' and c != '>' :
                parse += c
        if parse != "" :
            self.nonTerminals[len(self.nonTerminals) - 1].addRule(parse)

    def inputData(self) :
        #self.addRule("S -> Sa | Sb | c | d")
        self.addRule("v ->  Name | prefixexp [ exp ] | prefixexp . Name ")

    def solveNonImmediateLR(self, A, B) :
        nameA = A.getName()
        nameB = B.getName()

        rulesA = []
        rulesB = []
        newRulesA = []
        rulesA = A.getRules()
        rulesB = B.getRules()

        for rule in rulesA :
            if rule[0 : len(nameB)] == nameB :
                for rule1 in rulesB :
                    newRulesA.append(rule1 + rule[len(nameB) : ])
            else :
                newRulesA.append(rule)
        A.setRules(newRulesA)

    def solveImmediateLR(self, A) :
        name = A.getName()
        newName = name + "'"

        alphas = []
        betas = []
        rules = A.getRules()
        newRulesA = []
        newRulesA1 = []

        rules = A.getRules()

        # Checks if there is left recursion or not
        for rule in rules :
            if rule[0 : len(name)] == name :
                alphas.append(rule[len(name) : ])
            else :
                betas.append(rule)

        # If no left recursion, exit
        if len(alphas) == 0 :
            return

        if len(betas) == 0 :
            newRulesA.append(newName)

        for beta in betas :
            newRulesA.append(beta + newName)

        for alpha in alphas :
            newRulesA1.append(alpha + newName)

        # Amends the original rule

        A.setRules(newRulesA)
        newRulesA1.append("\u03B5")

        # Adds new production rule
        newNonTerminal = NonTerminal(newName)
        newNonTerminal.setRules(newRulesA1)
        self.nonTerminals.append(newNonTerminal)

    def applyAlgorithm(self) :
        size = len(self.nonTerminals)
        for i in range(size) :
            for j in range(i) :
                self.solveNonImmediateLR(self.nonTerminals[i], self.nonTerminals[j])
            self.solveImmediateLR(self.nonTerminals[i])

    def printRules(self) :
        for nonTerminal in self.nonTerminals :
            nonTerminal.printRule()

            
grammar = Grammar()
grammar.inputData()
grammar.applyAlgorithm()
grammar.printRules()