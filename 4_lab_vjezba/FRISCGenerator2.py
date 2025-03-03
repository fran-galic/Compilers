# raid 11 ali 20 ima timeout na 60 skedni ot je 16/20 tj otprilike = 4 boda od 5
import sys

##
## 1) Definicija podataka o čvorovima generativnog stabla
##    + Parsanje ulaza
##

class Node:
    """
    Pojedini čvor generativnog stabla.
    level    -> int, dubina uvučenosti (broj space-ova ispred)
    lex_type -> npr. "IDN", "BROJ", "KR_ZA", "OP_PRIDRUZI"...
    line_num -> int, broj retka u izvorniku (sam PPJ daje)
    value    -> string, npr. 'x', '=', '10'...
    children -> lista Node (kad gradimo AST, popunjavat ćemo)
    """
    def __init__(self, level, lex_type, line_num, value):
        self.level = level
        self.lex_type = lex_type
        self.line_num = line_num
        self.value = value
        self.children = []

    def __repr__(self):
        return (f"Node({self.lex_type},"
                f"{self.line_num},"
                f"{self.value},"
                f"level={self.level},"
                f"children={len(self.children)})")


def parse_input():
    """
    Pročita retke sa stdin, stvori listu Node.
    Neposredno "spajanje" roditelj-dijete radimo tek kad radimo AST.
    Ovdje samo punimo polje `nodes`.
    """
    nodes = []
    for line in sys.stdin:
        stripline = line.strip()
        if stripline == "" or stripline == "$":
            continue
        if stripline.startswith("<") and stripline.endswith(">"):
            # npr. <program> => za generativno stablo, mi ne trebamo Node
            continue

        # Inače, mora imati barem 3 dijela: "IDN 2 x"
        level = len(line) - len(line.lstrip())  # uvucenost
        parts = stripline.split()
        if len(parts) < 3:
            continue

        lex_type = parts[0]
        line_num = int(parts[1])
        value = " ".join(parts[2:])

        n = Node(level, lex_type, line_num, value)
        nodes.append(n)

    return nodes


##
## 2) AST definicije (klase) za naredbe i izraze
##

class ProgramAST:
    def __init__(self, stmts):
        self.stmts = stmts  # lista StatementAST

class StatementAST:
    """
    Bazna klasa za sve naredbe.
    """

class AssignAST(StatementAST):
    """
    Naredba pridruživanja: var = expr
    """
    def __init__(self, var_name, line_num, expr):
        self.var_name = var_name
        self.line_num = line_num
        self.expr = expr   # ExpressionAST

class ForAST(StatementAST):
    """
    Naredba za-petlje: za i od e1 do e2 ... az
    """
    def __init__(self, var_name, line_num, e1, e2, inner_stmts):
        self.var_name = var_name
        self.line_num = line_num
        self.e1 = e1  # ExpressionAST (od-izraz)
        self.e2 = e2  # ExpressionAST (do-izraz)
        self.inner_stmts = inner_stmts  # lista StatementAST


# Expression AST
class ExpressionAST:
    pass

class BinaryOpAST(ExpressionAST):
    """
    Binarna operacija: left op right
      op in {+, -, *, /}
    """
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpAST(ExpressionAST):
    """
    Unarni plus ili minus: +expr ili -expr
    """
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class NumAST(ExpressionAST):
    """
    Numerička konstanta (BROJ).
    """
    def __init__(self, value):
        # value je string "10", "123", ...
        self.value = int(value)  # pretvori u int

class VarAST(ExpressionAST):
    """
    Varijabla (IDN).
    """
    def __init__(self, name, line_num):
        self.name = name
        self.line_num = line_num


##
## 3) Strukture za semantiku (definirane varijable) i mapiranje var->mem
##

class DefinedIdentifier:
    def __init__(self, scope_level, line_def, name):
        self.scope_level = scope_level
        self.line_def = line_def
        self.name = name

list_defined = []      # popis DefinedIdentifier
scope_level = 0

# mapiranje (var_name, scope_level) -> label npr. "V0"
variable_map = {}
var_counter = 0


def alloc_var(name, scope):
    """
    Ako (name, scope) nema labelu, dodijeli V{var_counter}.
    Vrati taj label (string).
    """
    global var_counter
    key = (name, scope)
    if key not in variable_map:
        lbl = f"V{var_counter}"
        var_counter += 1
        variable_map[key] = lbl
    return variable_map[key]


def find_var_label(name):
    """
    Pretraži list_defined odostraga.
    Kad prvi put nadiđe name, dohvati (name, scope) iz variable_map.
    Vrati label ili None ako nije nađeno.
    """
    for d in reversed(list_defined):
        if d.name == name:
            k = (name, d.scope_level)
            return variable_map.get(k, None)
    return None


##
## 4) Gradnja AST-a iz popisa Node-ova + semantika
##    Pritom rješavamo:
##      - statemente:  <naredba_pridruzivanja>, <za_petlja>
##      - <E> (izrazi) -> rekurzivno do <T>, <P>, ...
##    Koristit ćemo klasični LL(1) ili slično, ali sada iz Node-ova
##
##    Za DEMO, radit ćemo linearno i tražiti pattern:
##      IDN ... '=' ... => AssignAST
##      KR_ZA => ForAST
##      ...
##    Dok ne potrošimo sve Node-ove.
##

def build_program_ast(nodes, start_index=0):
    """
    Parsiraj sve node-ove do kraja u listu naredbi (stmts).
    Vrati (ProgramAST, next_index).
    """
    stmts = []
    i = start_index
    n = len(nodes)

    global scope_level

    while i < n:
        node = nodes[i]

        # 1) KR_AZ => kraj for-bloka => break
        if node.lex_type == "KR_AZ":
            break

        # 2) KR_ZA => for-petlja
        if node.lex_type == "KR_ZA":
            scope_level += 1

            i += 1
            if i >= n:
                break
            brojac = nodes[i]
            if brojac.lex_type != "IDN":
                # greška, ali nastavimo
                break

            var_name = brojac.value
            line_num = brojac.line_num

            # Definiraj var_name u tom scopeu ako nije već
            already_def = any(
                (d.name == var_name and d.scope_level == scope_level)
                for d in list_defined
            )
            if not already_def:
                list_defined.append(DefinedIdentifier(scope_level, line_num, var_name))

            i += 1
            # sad očekujemo KR_OD
            if i < n and nodes[i].lex_type == "KR_OD":
                i += 1
                # parse E (od-izraz)
                (expr1, i) = parse_expression(nodes, i)
            else:
                expr1 = NumAST(0)  # fallback

            # sad KR_DO
            if i < n and nodes[i].lex_type == "KR_DO":
                i += 1
                (expr2, i) = parse_expression(nodes, i)
            else:
                expr2 = NumAST(0)

            # sad dolazi <lista_naredbi> dok ne naiđemo "KR_AZ"
            (inner_prog, i2) = build_program_ast(nodes, i)
            inner_stmts = inner_prog.stmts

            # kad izađemo, i2 pokazuje na KR_AZ => potrošimo ga
            if i2 < n and nodes[i2].lex_type == "KR_AZ":
                i2 += 1
            # smanji scope
            scope_level -= 1

            # obriši definicije iz list_defined za scope
            new_def_list = []
            for d in list_defined:
                if d.scope_level == scope_level + 1 and d.name == var_name:
                    pass
                else:
                    new_def_list.append(d)
            list_defined.clear()
            list_defined.extend(new_def_list)

            # stvori ForAST
            stmt = ForAST(var_name, line_num, expr1, expr2, inner_stmts)
            stmts.append(stmt)
            i = i2
            continue

        # 3) Ako je IDN i sljedeći je OP_PRIDRUZI '=', to je Assign
        if node.lex_type == "IDN":
            if i+1 < n and nodes[i+1].lex_type == "OP_PRIDRUZI":
                var_name = node.value
                line_num = node.line_num
                # definicija ako nije u ovom scopeu
                already_def = any(
                    (d.name == var_name and d.scope_level == scope_level)
                    for d in list_defined
                )
                if not already_def:
                    list_defined.append(DefinedIdentifier(scope_level, line_num, var_name))
                i += 2  # preskačemo '='
                (expr, i) = parse_expression(nodes, i)
                stmt = AssignAST(var_name, line_num, expr)
                stmts.append(stmt)
                continue

        # inače, samo preskači
        i += 1

    return (ProgramAST(stmts), i)


def parse_expression(nodes, start_i):
    """
    Rekurzivno parsiraj <E>, <T>, <P>.
     <E> ::= <T> <E_lista>
     <T> ::= <P> <T_lista>
     <P> ::= BROJ | IDN | ( <E> ) | OP_PLUS <P> | OP_MINUS <P>
     <E_lista> ::= (OP_PLUS|OP_MINUS) <T> <E_lista> | ε
     <T_lista> ::= (OP_PUTA|OP_DIJELI) <P> <T_lista> | ε
    """
    (left_node, idx_after_left) = parse_T(nodes, start_i)
    return parse_E_lista(nodes, idx_after_left, left_node)

def parse_E_lista(nodes, start_i, left_ast):
    i = start_i
    n = len(nodes)
    while i < n:
        tk = nodes[i]
        if tk.lex_type in ["OP_PLUS", "OP_MINUS"]:
            op = tk.value  # '+' ili '-'
            i += 1
            (right_ast, i) = parse_T(nodes, i)
            new_left = BinaryOpAST(left_ast, op, right_ast)
            left_ast = new_left
        else:
            break
    return (left_ast, i)

def parse_T(nodes, start_i):
    (left_node, idx_after_left) = parse_P(nodes, start_i)
    return parse_T_lista(nodes, idx_after_left, left_node)

def parse_T_lista(nodes, start_i, left_ast):
    i = start_i
    n = len(nodes)
    while i < n:
        tk = nodes[i]
        if tk.lex_type in ["OP_PUTA", "OP_DIJELI"]:
            op = tk.value  # '*' ili '/'
            i += 1
            (right_ast, i) = parse_P(nodes, i)
            new_left = BinaryOpAST(left_ast, op, right_ast)
            left_ast = new_left
        else:
            break
    return (left_ast, i)

def parse_P(nodes, start_i):
    if start_i >= len(nodes):
        return (NumAST(0), start_i)
    tk = nodes[start_i]
    if tk.lex_type == "BROJ":
        expr = NumAST(tk.value)
        return (expr, start_i+1)
    if tk.lex_type == "IDN":
        # provjeri definiranost
        found = False
        for d in reversed(list_defined):
            if d.name == tk.value:
                found = True
                break
        expr = VarAST(tk.value, tk.line_num)
        return (expr, start_i+1)
    if tk.lex_type in ["OP_PLUS", "OP_MINUS"]:
        op = tk.value  # '+' ili '-'
        i2 = start_i+1
        (subexpr, i3) = parse_P(nodes, i2)
        expr = UnaryOpAST(op, subexpr)
        return (expr, i3)

    # fallback
    return (NumAST(0), start_i+1)


##
## 5) Generiranje FRISC koda
##
frisc_file = open("a.frisc", "w")

def emit(line):
    frisc_file.write(line + "\n")

label_count = 0
def new_label(prefix="L"):
    global label_count
    s = f"{prefix}{label_count}"
    label_count += 1
    return s

def emit_push(reg):
    emit("  SUB R7, 4, R7")
    emit(f"  STORE {reg}, (R7)")

def emit_pop(reg):
    emit(f"  LOAD {reg}, (R7)")
    emit("  ADD R7, 4, R7")


def generate_program(prog_ast):
    for stmt in prog_ast.stmts:
        generate_statement(stmt)

def generate_statement(stmt):
    # 1) Naredba pridruživanja
    if isinstance(stmt, AssignAST):
        generate_expression(stmt.expr)  # stavi vrijednost expr na stog
        emit_pop("R0")                 # pop u R0
        lbl = find_var_label(stmt.var_name)
        if not lbl:
            # definiramo var globalno (ili u tekućem scopeu)
            lbl = alloc_var(stmt.var_name, 0)
        emit(f"  STORE R0, ({lbl})")

    # 2) Naredba petlje `za ... od e1 do e2`
    elif isinstance(stmt, ForAST):
        # 2.1) Inicijalizacija brojača (j = e1)
        generate_expression(stmt.e1)  # push
        emit_pop("R0")
        lbl = find_var_label(stmt.var_name)
        if not lbl:
            lbl = alloc_var(stmt.var_name, scope_level)
        emit(f"  STORE R0, ({lbl})")

        start_lab = new_label("petlja_")
        end_lab   = new_label("endp_")

        # 2.2) Početak tijela
        emit(f"{start_lab}")
        # 2.3) Generiraj tijelo
        for s in stmt.inner_stmts:
            generate_statement(s)

        # 2.4) Inkrement brojača
        emit(f"  LOAD R0, ({lbl})")
        emit("  ADD R0, 1, R0")
        emit(f"  STORE R0, ({lbl})")

        # 2.5) Ponovna evaluacija do-izraza (npr. i*i),
        #     generiraj kôd => push => pop R1
        generate_expression(stmt.e2)
        emit_pop("R1")

        # 2.6) Usporedi brojač (j) i do-izraz
        emit(f"  LOAD R0, ({lbl})")  # j
        emit("  SUB R1, R0, R2")     # R2 = do - j
        emit(f"  JP_N {end_lab}")    # ako do-j < 0 => kraj
        emit(f"  JP {start_lab}")
        emit(f"{end_lab}")

def generate_expression(expr):
    if isinstance(expr, NumAST):
        emit(f"  MOVE %D {expr.value}, R0")
        emit_push("R0")
    elif isinstance(expr, VarAST):
        lbl = find_var_label(expr.name)
        if not lbl:
            lbl = alloc_var(expr.name, 0)
        emit(f"  LOAD R0, ({lbl})")
        emit_push("R0")
    elif isinstance(expr, UnaryOpAST):
        generate_expression(expr.expr)
        emit_pop("R0")
        if expr.op == "-":
            emit("  XOR R0, -1, R0")
            emit("  ADD R0, 1, R0")
        emit_push("R0")
    elif isinstance(expr, BinaryOpAST):
        # generiraj left => stog
        generate_expression(expr.left)
        # generiraj right => stog
        generate_expression(expr.right)
        # pop R1, pop R0
        emit_pop("R1")
        emit_pop("R0")
        if expr.op == "+":
            emit("  ADD R0, R1, R2")
            emit_push("R2")
        elif expr.op == "-":
            emit("  SUB R0, R1, R2")
            emit_push("R2")
        elif expr.op == "*":
            # push R0, push R1, CALL MUL
            emit_push("R0")
            emit_push("R1")
            emit("  CALL MUL")
        elif expr.op == "/":
            emit_push("R0")
            emit_push("R1")
            emit("  CALL DIV")
        else:
            # fallback
            emit("  MOVE %D 0, R2")
            emit_push("R2")
    else:
        # fallback
        emit("  MOVE %D 0, R0")
        emit_push("R0")



nodes = parse_input()

(prog_ast, consumed) = build_program_ast(nodes, 0)

# Zaglavlje
emit("; ========== POCETAK PROGRAMA ===========")
emit("    MOVE 40000, R7   ; init stog")
emit("; ========== START MAIN ===========")

generate_program(prog_ast)

# Na kraju => LOAD R6,(rez) => HALT
rez_lbl = None
for d in list_defined:
    if d.name == "rez" and d.scope_level == 0:
        rez_lbl = variable_map.get(("rez", 0), None)
if not rez_lbl:
    rez_lbl = alloc_var("rez", 0)
emit(f"  LOAD R6, ({rez_lbl})")
emit("  HALT")

# Definicija varijabli
emit("; ========== DEKLARACIJA VARIJABLI ===========")
for (k, lbl) in variable_map.items():
    var_name, scp = k
    emit(f"{lbl}  DW 0   ; var={var_name}, scope={scp}")

# Potprogrami MUL, DIV
emit("; ========== POTPROGRAMI ZA MUL, DIV ===========")
emit("""\
;----------------------------------
;  potprogram MUL
;----------------------------------
MUL     CALL MD_INIT
        XOR R1, 0, R1
        JP_Z MUL_RET
        SUB R1, 1, R1
MUL_1   ADD R2, R0, R2
        SUB R1, 1, R1
        JP_NN MUL_1
MUL_RET CALL MD_RET
        RET

;----------------------------------
;  potprogram DIV
;----------------------------------
DIV     CALL MD_INIT
        XOR R1, 0, R1
        JP_Z DIV_RET
DIV_1   ADD R2, 1, R2
        SUB R0, R1, R0
        JP_NN DIV_1
        SUB R2, 1, R2
DIV_RET CALL MD_RET
        RET

;----------------------------------
;  potprogrami za M/D
;----------------------------------
MD_SGN  MOVE 0, R6
        XOR R0, 0, R0
        JP_P MD_TST1
        XOR R0, -1, R0
        ADD R0, 1, R0
        MOVE 1, R6
MD_TST1 XOR R1, 0, R1
        JP_P MD_SGNR
        XOR R1, -1, R1
        ADD R1, 1, R1
        XOR R6, 1, R6
MD_SGNR RET

MD_INIT POP R4
        POP R3
        POP R1
        POP R0
        CALL MD_SGN
        MOVE 0, R2
        PUSH R4
        RET

MD_RET  XOR R6, 0, R6
        JP_Z MD_RET1
        XOR R2, -1, R2
        ADD R2, 1, R2
MD_RET1 POP R4
        PUSH R2
        PUSH R3
        PUSH R4
        RET
""")

frisc_file.close()



