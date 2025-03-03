import sys
# rade svi osim 11, 12, 16 i 18, to je nekih 4 bod aod 5

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

def parse_input():
    nodes = []
    
    for line in sys.stdin:
        stripped_line = line.strip()

        if stripped_line.startswith('<') and stripped_line.endswith('>') or stripped_line == "$":
            continue

        level = len(line) - len(line.lstrip())

        parts = stripped_line.split()
        if len(parts) < 3:
            continue 

        lex_type = parts[0]
        line_num = int(parts[1])
        value = " ".join(parts[2:])

        nodes.append(Node(level, lex_type, line_num, value))

    return nodes

class DefinedIdentifierNode:
    def __init__(self, visibility_level, definition_line, value):
        self.visibility_level = visibility_level
        self.definition_line = definition_line
        self.value = value

    def __repr__(self):
        return f"visibility_level: {self.visibility_level}, definition_line: {self.definition_line}, value: {self.value}"

# glavni dio koda:
lista_ulaznih_podataka = parse_input()

lista_definiranih = []
razina_vidljivosti = 0
redak_koji_se_provjerava = 0
znak_koji_se_provjerava = "\0"


for index, ulazni_podatak in enumerate(lista_ulaznih_podataka):
   pravilno_je_definiran = False

   if index != len(lista_ulaznih_podataka) - 1:
      if ulazni_podatak.lex_type == "IDN" and lista_ulaznih_podataka[index + 1].value == "=":
            if not any(definedNode.value == ulazni_podatak.value for definedNode in lista_definiranih):
               lista_definiranih.append(DefinedIdentifierNode(razina_vidljivosti, ulazni_podatak.line_num, ulazni_podatak.value))
               redak_koji_se_provjerava = ulazni_podatak.line_num
               znak_koji_se_provjerava = ulazni_podatak.value

      elif ulazni_podatak.lex_type == "IDN" and index != 0 and lista_ulaznih_podataka[index - 1].lex_type == "KR_ZA":
            # treba provjeriti dali se do kraja retka nalazi ijendom tja isti znak
            # to mozda treba i nekkao sve do tijela funckije sot nezma kako bi
            redak_koji_se_provjerava = ulazni_podatak.line_num
            znak_koji_se_provjerava = ulazni_podatak.value

            razina_vidljivosti += 1
            lista_definiranih.append(DefinedIdentifierNode(razina_vidljivosti, ulazni_podatak.line_num, ulazni_podatak.value))

      elif ulazni_podatak.lex_type == "IDN":
            # ukoliko se u isotm redu u za peltji nalazi znak koji se tke definrirao onda baci gresku, vjeorvatno bi trebalo radit cak i ak se za peltja prelomi mozda
            if(ulazni_podatak.line_num == redak_koji_se_provjerava and ulazni_podatak.value == znak_koji_se_provjerava):
               print(f"err {ulazni_podatak.line_num} {ulazni_podatak.value}")
               break
            for defined_node in reversed(lista_definiranih):
               if ulazni_podatak.value == defined_node.value:
                  print(f"{ulazni_podatak.line_num} {defined_node.definition_line} {ulazni_podatak.value}")
                  pravilno_je_definiran = True
                  break
            if not pravilno_je_definiran:
               print(f"err {ulazni_podatak.line_num} {ulazni_podatak.value}")
               break

      elif ulazni_podatak.lex_type == "KR_AZ":
            lista_definiranih = list(filter(lambda definirani_podatak: definirani_podatak.visibility_level < razina_vidljivosti, lista_definiranih))
            razina_vidljivosti -= 1

   if index == len(lista_ulaznih_podataka) - 1:
      if ulazni_podatak.lex_type == "IDN":
            for defined_node in reversed(lista_definiranih):
               if ulazni_podatak.value == defined_node.value:
                  print(f"{ulazni_podatak.line_num} {defined_node.definition_line} {ulazni_podatak.value}")
                  pravilno_je_definiran = True
                  break
            if not pravilno_je_definiran:
               print(f"err {ulazni_podatak.line_num} {ulazni_podatak.value}")
               break

      elif ulazni_podatak.lex_type == "KR_AZ":
            lista_definiranih = list(filter(lambda definirani_podatak: definirani_podatak.visibility_level < razina_vidljivosti, lista_definiranih))
            razina_vidljivosti -= 1
