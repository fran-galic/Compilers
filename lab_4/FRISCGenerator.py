# !!! ovo predajem - radi u 16/20 posot slucajeva ako se dogdi timeout na 20 testu ili ako se ne dogodi onda 17/20, sot je od 4/5 do 4.25/5 bdoova s cime sam cisot zadovoljan
import sys

##
## 1) Definicija čvorova i parse_input
##

class Node:
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
    nodes = []
    for line in sys.stdin:
        stripline = line.strip()
        if not stripline or stripline == "$":
            continue
        if stripline.startswith("<") and stripline.endswith(">"):
            # preskačemo npr. <program>, <lista_naredbi>...
            continue

        level = len(line) - len(line.lstrip())
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
## 2) AST klase
##

class ProgramAST:
    def __init__(self, stmts):
        self.stmts = stmts

class StatementAST:
    pass

class AssignAST(StatementAST):
    def __init__(self, var_name, line_num, expr):
        self.var_name = var_name
        self.line_num = line_num
        self.expr = expr  # ExpressionAST

class ForAST(StatementAST):
    def __init__(self, var_name, line_num, e1, e2, inner_stmts):
        self.var_name = var_name
        self.line_num = line_num
        self.e1 = e1
        self.e2 = e2
        self.inner_stmts = inner_stmts

#
# Expressions
#

class ExpressionAST:
    pass

class BinaryOpAST(ExpressionAST):
    def __init__(self, left, op, right):
        self.left = left
        self.op   = op
        self.right= right

class UnaryOpAST(ExpressionAST):
    def __init__(self, op, expr):
        self.op   = op
        self.expr = expr

class NumAST(ExpressionAST):
    def __init__(self, val_str):
        self.value = int(val_str)

class VarAST(ExpressionAST):
    def __init__(self, name, line_num):
        self.name = name
        self.line_num = line_num


##
## 3) Strukture za semantiku i mapiranje
##

class DefinedIdentifier:
    def __init__(self, scope_level, line_def, name):
        self.scope_level = scope_level
        self.line_def    = line_def
        self.name        = name

list_defined = []
scope_level  = 0

variable_map = {}
var_counter  = 0

def alloc_var(name, scope):
    global var_counter
    key = (name, scope)
    if key not in variable_map:
        label = f"V{var_counter}"
        var_counter += 1
        variable_map[key] = label
    return variable_map[key]

def find_var_label(name):
    # pretraži list_defined odostraga (dublji scope prije)
    for d in reversed(list_defined):
        if d.name == name:
            k = (name, d.scope_level)
            return variable_map.get(k, None)
    return None


##
## 4) Gradnja AST
##

def build_program_ast(nodes, start_i=0):
    stmts = []
    i = start_i
    n = len(nodes)

    global scope_level

    while i<n:
        nd = nodes[i]

        # KR_AZ => break
        if nd.lex_type == "KR_AZ":
            break

        # KR_ZA => for-petlja
        if nd.lex_type == "KR_ZA":
            scope_level += 1
            i+=1
            if i>=n: 
                break
            brojac = nodes[i]
            if brojac.lex_type!="IDN":
                break
            var_name = brojac.value
            line_num = brojac.line_num
            i+=1

            # stvori *NOVU* definiciju u trenutačnom scopeu (ako nema u tom scopeu)
            same_scope_def = any(
                (d.name==var_name and d.scope_level==scope_level)
                for d in list_defined
            )
            if not same_scope_def:
                list_defined.append(DefinedIdentifier(scope_level,line_num,var_name))

            # KR_OD
            if i<n and nodes[i].lex_type=="KR_OD":
                i+=1
                (expr1, i) = parse_expression(nodes, i)
            else:
                expr1=NumAST("0")

            # KR_DO
            if i<n and nodes[i].lex_type=="KR_DO":
                i+=1
                (expr2,i) = parse_expression(nodes,i)
            else:
                expr2=NumAST("0")

            # parse <lista_naredbi> do KR_AZ
            (inner_prog, i2) = build_program_ast(nodes,i)
            inner_stmts=inner_prog.stmts

            # potroši KR_AZ
            if i2<n and nodes[i2].lex_type=="KR_AZ":
                i2+=1

            # sada izlazimo iz scopea
            old_scope = scope_level
            scope_level-=1

            # obriši definicije scope=old_scope
            new_list=[]
            for d in list_defined:
                if d.scope_level==old_scope:
                    # briši
                    pass
                else:
                    new_list.append(d)
            list_defined.clear()
            list_defined.extend(new_list)

            stmt= ForAST(var_name,line_num, expr1, expr2, inner_stmts)
            stmts.append(stmt)
            i=i2
            continue

        # Ako IDN i '=' => assign
        if nd.lex_type=="IDN":
            if i+1<n and nodes[i+1].lex_type=="OP_PRIDRUZI":
                var_name = nd.value
                line_num = nd.line_num
                i+=2
                (expr, i) = parse_expression(nodes,i)
                # ako nema definicije u scopeu => stvori
                same_scope_def = any(
                    (d.name==var_name and d.scope_level==scope_level)
                    for d in list_defined
                )
                if not same_scope_def:
                    list_defined.append(DefinedIdentifier(scope_level,line_num,var_name))
                stmt=AssignAST(var_name,line_num,expr)
                stmts.append(stmt)
                continue

        i+=1

    return (ProgramAST(stmts), i)


def parse_expression(nodes, start_i):
    (left, i2)=parse_T(nodes,start_i)
    return parse_E_lista(nodes,i2,left)

def parse_E_lista(nodes,start_i,left_ast):
    i = start_i
    n = len(nodes)
    while i<n:
        tk=nodes[i]
        if tk.lex_type in ["OP_PLUS","OP_MINUS"]:
            op = tk.value
            i+=1
            (right_ast, i)=parse_T(nodes,i)
            left_ast=BinaryOpAST(left_ast,op,right_ast)
        else:
            break
    return (left_ast,i)

def parse_T(nodes,start_i):
    (left, i2)=parse_P(nodes,start_i)
    return parse_T_lista(nodes,i2,left)

def parse_T_lista(nodes,start_i,left_ast):
    i = start_i
    n = len(nodes)
    while i<n:
        tk=nodes[i]
        if tk.lex_type in ["OP_PUTA","OP_DIJELI"]:
            op = tk.value
            i+=1
            (right_ast, i)=parse_P(nodes,i)
            left_ast=BinaryOpAST(left_ast,op,right_ast)
        else:
            break
    return (left_ast,i)

def parse_P(nodes,start_i):
    if start_i>=len(nodes):
        return (NumAST("0"), start_i)
    tk=nodes[start_i]
    if tk.lex_type=="BROJ":
        return (NumAST(tk.value), start_i+1)
    if tk.lex_type=="IDN":
        return (VarAST(tk.value,tk.line_num), start_i+1)
    if tk.lex_type in ["OP_PLUS","OP_MINUS"]:
        op = tk.value
        (sube, i2)=parse_P(nodes,start_i+1)
        return (UnaryOpAST(op,sube), i2)
    # fallback
    return (NumAST("0"), start_i+1)

##
## 5) Generiranje FRISC
##
frisc_file = open("a.frisc","w")

def emit(line):
    frisc_file.write(line+"\n")

label_counter=0
def new_label(prefix="L"):
    global label_counter
    s=f"{prefix}{label_counter}"
    label_counter+=1
    return s

def emit_push(reg):
    emit("  SUB R7, 4, R7")
    emit(f"  STORE {reg}, (R7)")

def emit_pop(reg):
    emit(f"  LOAD {reg}, (R7)")
    emit("  ADD R7, 4, R7")

def generate_program(prog_ast):
    for st in prog_ast.stmts:
        generate_statement(st)

def generate_statement(stmt):
    if isinstance(stmt, AssignAST):
        # generiraj expr => push
        generate_expression(stmt.expr)
        emit_pop("R0")
        lbl = find_var_label(stmt.var_name)
        if not lbl:
            # fallback: globalno
            lbl = alloc_var(stmt.var_name,0)
        emit(f"  STORE R0, ({lbl})")

    elif isinstance(stmt, ForAST):
        # inicijalizacija
        generate_expression(stmt.e1)
        emit_pop("R0")
        lbl = find_var_label(stmt.var_name)
        if not lbl:
            lbl= alloc_var(stmt.var_name,0)
        emit(f"  STORE R0, ({lbl})")

        startL=new_label("PETLJA_")
        endL  =new_label("END_")

        emit(f"{startL}")
        # tijelo
        for s in stmt.inner_stmts:
            generate_statement(s)

        # brojac++
        emit(f"  LOAD R0, ({lbl})")
        emit("  ADD R0, 1, R0")
        emit(f"  STORE R0, ({lbl})")

        # do-izraz
        generate_expression(stmt.e2)
        emit_pop("R1")

        emit(f"  LOAD R0, ({lbl})")
        emit("  SUB R1, R0, R2")
        emit(f"  JP_N {endL}")
        emit(f"  JP {startL}")
        emit(f"{endL}")

def generate_expression(expr):
    if isinstance(expr, NumAST):
        emit(f"  MOVE %D {expr.value}, R0")
        emit_push("R0")
    elif isinstance(expr, VarAST):
        lbl = find_var_label(expr.name)
        if not lbl:
            lbl=alloc_var(expr.name,0)
        emit(f"  LOAD R0, ({lbl})")
        emit_push("R0")
    elif isinstance(expr, UnaryOpAST):
        generate_expression(expr.expr)
        emit_pop("R0")
        if expr.op=="-":
            emit("  XOR R0, -1, R0")
            emit("  ADD R0, 1, R0")
        emit_push("R0")
    elif isinstance(expr, BinaryOpAST):
        generate_expression(expr.left)
        generate_expression(expr.right)
        emit_pop("R1")
        emit_pop("R0")
        if expr.op=="+":
            emit("  ADD R0, R1, R2")
            emit_push("R2")
        elif expr.op=="-":
            emit("  SUB R0, R1, R2")
            emit_push("R2")
        elif expr.op=="*":
            emit_push("R0")
            emit_push("R1")
            emit("  CALL MUL")
        elif expr.op=="/":
            emit_push("R0")
            emit_push("R1")
            emit("  CALL DIV")
        else:
            emit("  MOVE %D 0, R2")
            emit_push("R2")
    else:
        # fallback
        emit("  MOVE %D 0, R0")
        emit_push("R0")


nodes = parse_input()
(prog_ast, usedi)= build_program_ast(nodes,0)

emit("; ========== POCETAK PROGRAMA ===========")
emit("    MOVE 40000, R7   ; init stog")
emit("; ========== START MAIN ===========")

generate_program(prog_ast)

# load rez => HALT
rez_lbl = None
for d in list_defined:
    if d.name=="rez" and d.scope_level==0:
        rez_lbl = variable_map.get((d.name, 0), None)
if not rez_lbl:
    rez_lbl=alloc_var("rez",0)

emit(f"  LOAD R6, ({rez_lbl})")
emit("  HALT")

# varijable
emit("; ========== DEKLARACIJA VARIJABLI ===========")
for (k,v) in variable_map.items():
    nm,scp = k
    emit(f"{v}  DW 0   ; var={nm}, scope={scp}")

# MULL, DIV
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

