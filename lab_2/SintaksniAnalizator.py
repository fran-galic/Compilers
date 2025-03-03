import sys

#funkcije:
def je_li_nezavrsni(string):
    izrazi = [
        '<program>',
        '<lista_naredbi>',
        '<naredba>',
        '<naredba_pridruzivanja>',
        '<za_petlja>',
        '<E>',
        '<E_lista>',
        '<T>',
        '<T_lista>',
        '<P>'
    ]

    # Provjera je li string u listi izraza
    return string in izrazi

def je_li_zavrsni(string):
    zavrsni_izrazi = [
        'IDN',
        'BROJ',
        'OP_PRIDRUZI',
        'OP_PLUS',
        'OP_MINUS',
        'OP_PUTA',
        'OP_DIJELI',
        'L_ZAGRADA',
        'D_ZAGRADA',
        'KR_ZA',
        'KR_OD',
        'KR_DO',
        'KR_AZ'
    ]

    # Provjera je li string u listi zavrsnih izraza
    return string in zavrsni_izrazi

def je_li_epsilon(string):
    return string == "$"


# strukture podataka:
znakovi_stoga = {
    '<program>': 0,
    '<lista_naredbi>': 1,
    '<naredba>': 2,
    '<naredba_pridruzivanja>': 3,
    '<za_petlja>': 4,
    '<E>': 5,
    '<E_lista>': 6,
    '<T>': 7,
    '<T_lista>': 8,
    '<P>': 9,
    'OP_PRIDRUZI': 10,
    'IDN': 11,
    'KR_OD': 12,
    'KR_DO': 13,
    'KR_AZ': 14,
    'D_ZAGRADA': 15,
    'dno_stoga': 16
}
unif_znakovi_ul_niza = {
    'IDN': 0,
    'BROJ': 1,
    'OP_PRIDRUZI': 2,
    'OP_PLUS': 3,
    'OP_MINUS': 4,
    'OP_PUTA': 5,
    'OP_DIJELI': 6,
    'L_ZAGRADA': 7,
    'D_ZAGRADA': 8,
    'KR_ZA': 9,
    'KR_OD': 10,
    'KR_DO': 11,
    'KR_AZ': 12,
    'kraj_niza': 13
}
funkcija_prijelaza = [
    ["<lista_naredbi>", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "<lista_naredbi>", "-1", "-1", "-1", "<lista_naredbi>"],
    ["<naredba> <lista_naredbi>", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "<naredba> <lista_naredbi>", "-1", "-1", "$", "$"],
    ["<naredba_pridruzivanja>", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "<za_petlja>", "-1", "-1", "-1", "-1"],
    ["IDN OP_PRIDRUZI <E>", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "KR_ZA IDN KR_OD <E> KR_DO <E> <lista_naredbi> KR_AZ", "-1", "-1", "-1", "-1"],
    ["<T> <E_lista>", "<T> <E_lista>", "-1", "<T> <E_lista>", "<T> <E_lista>", "-1", "-1", "<T> <E_lista>", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["$", "-1", "-1", "OP_PLUS <E>", "OP_MINUS <E>", "-1", "-1", "-1", "$", "$", "-1", "$", "$", "$"],
    ["<P> <T_lista>", "<P> <T_lista>", "-1", "<P> <T_lista>", "<P> <T_lista>", "-1", "-1", "<P> <T_lista>", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["$", "-1", "-1", "$", "$", "OP_PUTA <T>", "OP_DIJELI <T>", "-1", "$", "$", "-1", "$", "$", "$"],
    ["IDN", "BROJ", "-1", "OP_PLUS <P>", "OP_MINUS <P>", "-1", "-1", "L_ZAGRADA <E> D_ZAGRADA", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["-1", "-1", "", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "", "-1", "-1", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "", "-1", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "", "-1", "-1", "-1", "-1", "-1"],
    ["-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "-1", "0"]
]

# definiranje varijabli i struktura podataka:
program_gotov = False
stog = ["dno_stoga", "<program>"] # pocetni nezvarsni znak kao prvi znak na stogu
dubina = 0 # inicijalna dubljina stabla
generirano_stablo = [] # dodajem stringove u njega, kasnije ih sve spojim sa ''.join(generirano_stablo)

# glavni program
input_text = sys.stdin.read()
polje_ulaznih_znakova = input_text.strip().split("\n")
polje_ulaznih_znakova.append("kraj_niza")
# print(polje_ulaznih_znakova)
# print(stog)
# print()
# print()

while not program_gotov:
    # print(stog)
    #1. korak - procitaj znak sa stoga; mkani ga
    vrh_stoga = stog.pop()
    # print(stog)
    #2. korak - procitaj koliko ima praznina; makni ih
    while stog and stog[-1] == " ":  # nadi trenutnu dubinu znaka stoga
        stog.pop()  # Uklanjanje praznine sa stoga
        dubina += 1  # Povećavanje broja praznina
    #3. korak - ispisi u spremnik dubina * praznina + odgovarajuci cvor + \n
    if (vrh_stoga != "dno_stoga"):
        if (je_li_nezavrsni(vrh_stoga)):
            redak_stabla = " " * dubina + vrh_stoga + "\n"
            generirano_stablo.append(redak_stabla)
        if (je_li_zavrsni(vrh_stoga)):
            redak_stabla = " " * dubina + vrh_stoga + " "
            generirano_stablo.append(redak_stabla)
    # print(generirano_stablo)
    #4. korak - povecaj dubinu za 1
    dubina += 1

    #5. korak
    ulazni_znak = polje_ulaznih_znakova[0].split(" ")[0]   # !!!! po potrebi cu morat mkanut tja prvi element kansije
    # print(f"ulazni znak: {ulazni_znak}")
    DS_produkcije = funkcija_prijelaza[znakovi_stoga[vrh_stoga]][unif_znakovi_ul_niza[ulazni_znak]]
    # print(DS_produkcije)

    #6. korak - ovisno o tome sta smo dobili kao DS_produkcije raidmo različite stvari
    if (DS_produkcije == "0"):     # uspjeh
        print(''.join(generirano_stablo)) # ispisi stablo na stdout
        program_gotov = True
    elif (DS_produkcije == "-1"):   # postoji sintaksna greska
        program_gotov = True
        if polje_ulaznih_znakova[0] == "kraj_niza":
            print("err kraj")
        else:
            print(f"err {polje_ulaznih_znakova[0]}")
    elif je_li_nezavrsni(DS_produkcije.split(" ")[0]):
        for element in reversed(DS_produkcije.split(" ")):
            # Dodaj onoliko praznina " " na stog koliko je vrijednost varijable dubina
            for _ in range(dubina):
                stog.append(" ")  # Dodaj prazninu kao element stoga
            # Dodaj element na stog
            stog.append(element)
        # nemoramo micat prvi ulazni znak jer ga nismo zapravo konzumirali
        dubina = 0      # resetiramo dubinu
        # print(stog)

    elif je_li_zavrsni(DS_produkcije.split(" ")[0]):
        redak_stabla = " " * dubina + polje_ulaznih_znakova[0] + "\n"   # prije je bilo DS_produkcije.split(" ")[0]
        generirano_stablo.append(redak_stabla)
        ostatak_produkcija = DS_produkcije.split(" ")[1:]   # uzmi ostatak znakova s DS produkcije osim prvog
        for element in reversed(ostatak_produkcija):
            # Dodaj onoliko praznina " " na stog koliko je vrijednost varijable dubina
            for _ in range(dubina):
                stog.append(" ")  # Dodaj prazninu kao element stoga
            # Dodaj element na stog
            stog.append(element)
        dubina = 0
        polje_ulaznih_znakova = polje_ulaznih_znakova[1:] # izbaci prvi element iz polja jer si ga sad obradio

    elif je_li_epsilon(DS_produkcije.split(" ")[0]):
        redak_stabla = " " * dubina + DS_produkcije.split(" ")[0] + "\n"
        generirano_stablo.append(redak_stabla)
        dubina = 0
        # zadrzavamo se na istom ulaznom znaku

    elif DS_produkcije == "":
        dubina = 0
        redak_stabla = polje_ulaznih_znakova[0].split(" ")[1] + " " + polje_ulaznih_znakova[0].split(" ")[2] + "\n"
        generirano_stablo.append(redak_stabla)
        polje_ulaznih_znakova = polje_ulaznih_znakova[1:]  # izbaci prvi element iz polja jer si ga sad obradio

    else:
        print("Dogodila se neka gadna pogreska")
        program_gotov = True




