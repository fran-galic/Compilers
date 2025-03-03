class Node:
    def __init__(self, level, lex_type, line_num, value):
        self.level = level
        self.lex_type = lex_type
        self.line_num = line_num
        self.value = value

    def __repr__(self):
        base_output = f"{' ' * self.level}{self.lex_type} {self.line_num} {self.value}"
        padding = ' ' * (100 - len(base_output) - len(f" - razina hijerarhije: {self.level:3}"))
        return f"{base_output}{padding}- razina hijerarhije: {self.level:3}".rstrip()


def parse_file(file_path):
    nodes = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            #print(f"stripped line: {stripped_line}");

            if stripped_line.startswith('<') and stripped_line.endswith('>') or stripped_line == "$":
                continue

            level = len(line) - len(line.lstrip())

            parts = stripped_line.split()
            if len(parts) < 3:
                #print("Dogodila se greska u učitavanju podataka. Broj komponenti je manji od 3")
                #print(parts)
                continue 

            lex_type = parts[0]
            line_num = int(parts[1])
            value = " ".join(parts[2:]) # !!!

            # Create a Node and add it to the list
            nodes.append(Node(level, lex_type, line_num, value))

    return nodes


file_path = "./primjer/Test.in"  # Replace with your actual file path
lista_ulaznih_podataka = parse_file(file_path)

""" for node in lista_ulaznih_podataka:
    print(node) """


# glavni dio programa:
class DefinedIdentifierNode:
    def __init__(self, visibility_level, definition_line, value):
        self.visibility_level = visibility_level
        self.definition_line = definition_line
        self.value = value

    def __repr__(self):
        return f"visibility_level: {self.visibility_level}, definition_line: {self.definition_line}, value: {self.value}"

lista_definiranih = []
razina_vidljivosti = 0

for index, ulazni_podatak in enumerate(lista_ulaznih_podataka):
    # ako znak nije zadnji
    if(index != len(lista_ulaznih_podataka) - 1):
        pravilno_je_definiran = False
        # ako je procitan idetifikator s lijeve strane zagrade
        if(ulazni_podatak.lex_type == "IDN" and lista_ulaznih_podataka[index + 1].value == "="):
            #ako se ne nalazi vec u listi dodaj ga u lsitu definiranih, inace ignore
            if not any(definedNode.value == ulazni_podatak.value for definedNode in lista_definiranih):
                lista_definiranih.append(DefinedIdentifierNode(razina_vidljivosti, ulazni_podatak.line_num, ulazni_podatak.value))
            # else ignore;   ako vec postoji u listi definiranih

        # ako je IDN i prosli mu je bio za
        elif(ulazni_podatak.lex_type == "IDN" and index != 0 and lista_ulaznih_podataka[index - 1].lex_type == "KR_ZA"):
            razina_vidljivosti += 1
            lista_definiranih.append(DefinedIdentifierNode(razina_vidljivosti, ulazni_podatak.line_num, ulazni_podatak.value))

        elif(ulazni_podatak.lex_type == "IDN"):
            # iteriraj po lsiit definirnaih odnazad i vidi dali se pojavluje:
            for defined_node in reversed(lista_definiranih):
                if(ulazni_podatak.value == defined_node.value):
                    print(f"{ulazni_podatak.line_num} {defined_node.definition_line} {ulazni_podatak.value}")
                    pravilno_je_definiran = True
                    break
            if(not pravilno_je_definiran):
                print(f"err {ulazni_podatak.line_num} {ulazni_podatak.value}")
                break
        
        elif(ulazni_podatak.lex_type == "KR_AZ"):
            # makni sve koji imaju trenutnu razinu vidljivosti
            lista_definiranih = list(filter(lambda definirani_podatak: definirani_podatak.visibility_level < razina_vidljivosti, lista_definiranih))
            razina_vidljivosti -= 1

    if(index == len(lista_ulaznih_podataka) - 1):
        if(ulazni_podatak.lex_type == "IDN"):
            # iteriraj po lsiit definirnaih odnazad i vidi dali se pojavluje:
            for defined_node in reversed(lista_definiranih):
                if(ulazni_podatak.value == defined_node.value):
                    print(f"{ulazni_podatak.line_num} {defined_node.definition_line} {ulazni_podatak.value}")
                    pravilno_je_definiran = True
                    break
            if(not pravilno_je_definiran):
                print(f"err {ulazni_podatak.line_num} {ulazni_podatak.value}")
                break

        elif(ulazni_podatak.lex_type == "KR_AZ"):
            # makni sve koji imaju trenutnu razinu vidljivosti
            lista_definiranih = list(filter(lambda definirani_podatak: definirani_podatak.visibility_level < razina_vidljivosti, lista_definiranih))
            razina_vidljivosti -= 1