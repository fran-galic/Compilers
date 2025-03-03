import sys

def obradi_izraz(izraz, rbr_redka):
    i = 0

    while i < len(izraz):
        if izraz[i].isalpha():
            temp = izraz[i]
            i += 1
            while i < len(izraz) and (izraz[i].isalnum()):
                temp += izraz[i]
                i += 1
            print(f"IDN {rbr_redka} {temp}")

        elif izraz[i].isnumeric():
            temp = izraz[i]
            i += 1
            while i < len(izraz) and (izraz[i].isnumeric()):
                temp += izraz[i]
                i += 1
            print(f"BROJ {rbr_redka} {temp}")

        else:
            if i is not len(izraz) - 1 and izraz[i] == "/" and izraz[i + 1] == "/":
                return True
            elif izraz[i] == "=":
                print(f"OP_PRIDRUZI {rbr_redka} =")
            elif izraz[i] == "+":
                print(f"OP_PLUS {rbr_redka} +")
            elif izraz[i] == "-":
                print(f"OP_MINUS {rbr_redka} -")
            elif izraz[i] == "*":
                print(f"OP_PUTA {rbr_redka} *")
            elif izraz[i] == "/":
                print(f"OP_DIJELI {rbr_redka} /")
            elif izraz[i] == "(":
                print(f"L_ZAGRADA {rbr_redka} (")
            elif izraz[i] == ")":
                print(f"D_ZAGRADA {rbr_redka} )")
            else:
                print("NE odgovara sintaksi")
            i += 1
    return False

# Čitanje svega sa standardnog ulaza
input_tekst = sys.stdin.read()
rbr_redka = 0

# Ispis pročitanih podataka
# print("Pročitani podaci:\n")
# print(input_tekst)

polje_redaka = input_tekst.split("\n")
# print(polje_redaka)

for redak in polje_redaka:
    rbr_redka += 1
    polje_izraza = redak.split()
    # print(f"polje izraza je: {polje_izraza}")

    for izraz in polje_izraza:
        # provjera kljucnih rjeci
        if izraz == "za":
            print(f"KR_ZA {rbr_redka} za")
        elif izraz == "od":
            print(f"KR_OD {rbr_redka} od")
        elif izraz == "do":
            print(f"KR_DO {rbr_redka} do")
        elif izraz == "az":
            print(f"KR_AZ {rbr_redka} az")

        else:
            izraz_je_komentar = obradi_izraz(izraz, rbr_redka)
            if izraz_je_komentar:
                break