"""
Dati enter dupa fiecare solutie afisata.

"""

import copy
import sys
import time
import os
# primul argument este fisierul cu codul sursa
input_files = sys.argv[1]  # al doilea argument din apel, adica folderul ce contine fisierele cu input-ul
output_files = sys.argv[2]  # al treilea argument din apel, adica folderul ce contine fisierele cu output-ul
numar_solutii = int(sys.argv[3])  # al patrulea argument, numarul de solutii cautate
timp_timeout = float(sys.argv[4])  # al saselea argument, timpul de timeout
euristica = "euristica banala"

lista_fisiere = os.listdir("input_files")

# daca folderul cu fisierele de output nu exista, il cream
if not os.path.exists("output_files"):
    os.mkdir("output_files")

# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    def __init__(self, info, parinte, floriStatus, rageFlori, floriNr, culese, cost=0, h=0, lis=[]):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h
        self.floriStatus = floriStatus
        self.rageFlori = rageFlori
        self.floriNr = floriNr
        self.culese = culese
        self.lis = lis

    def obtineDrum(self):
        l = [self];
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for i, nod in enumerate(l):
            fout.write(f"{i + 1}" + ")\n" + "cost:" + f"{nod.g}" + "\n" + str(nod))
        if afisCost:
            fout.write("Cost: " + f"{self.g}\n")
        if afisCost:
            fout.write("Lungime: " + f"{len(l)}\n")
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return (sir)

    # euristica banală: daca nu e stare scop, returnez 1, altfel 0

    def __str__(self):
        sir = ""
        for linie in self.info:
            sir += " ".join([str(elem) for elem in linie]) + "\n"
        sir += f"{self.lis}\n"
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        f = open(nume_fisier, "r")
        sirFisier = f.read()
        listaLinii = sirFisier.strip().split("gradina")
        x = listaLinii[0].strip().split("\n")
        self.floriStatus = []
        cnt = 0
        for i in x:
            x[cnt] = x[cnt].split(" ")
            cnt += 1
        for i in x:
            self.floriStatus.append([i[0], int(i[1]), int(i[2])])
            #floriStatus retine tip_floare timp_treaza timp_adormita
        print(self.floriStatus)
        lung = len(self.floriStatus)
        self.rageFlori = []
        for i in range(lung):
            self.rageFlori.append(1)
        print(self.rageFlori)
        listaLinii.pop(0)
        listaLinii = listaLinii[0].split("buchet") #citirea de matrice
        a = listaLinii[0].strip().split("\n")
        self.start = []
        for i in a:
            self.start.append([x for x in i])
        print("START")
        print(self.start)  #matricea din input
        print("START")
        a = listaLinii[1].strip().split("\n")
        self.scopuri = []
        cnt = 0
        for i in a:
            a[cnt] = a[cnt].split(" ")
            cnt += 1
        for i in a:
            self.scopuri.append([i[0], int(i[1])])
        print("SCOPURI")
        print(self.scopuri) #nr de flori din buchet
        print("SCOPURI")
        self.culese = 0
        self.total = 0
        for i in range(len(self.scopuri)):
            self.total += self.scopuri[i][1]
        print("Total")
        print(self.total)  #nr total de flori din buchetul scop
        print("Total")
        self.noSol = 0
        for k in self.scopuri:
            add = 0
            for i in range(len(self.start)):
                for j in range(len(self.start[0])):
                    if self.start[i][j] == k[0]:
                        add += 1
            if add < k[1]:
                self.noSol = 1  #validare

#primeste ca parametru un nod si verifica daca se afla in starea finala sau nu
    #returneaza True sau False
    def testeaza_scop(self, nodCurent):
        for i in nodCurent.floriNr:
            if i[1] != 0:
                return 0
        return 1

    # va genera succesorii sub forma de noduri in arborele de parcurgere

    def checkPos(self, x, y, rage, mat, scop):
        if mat[x][y] == '.':  #pozitie buna daca e spatiu fara floare
            return 1
        tip = mat[x][y].lower() #daca nu e spatiu liber, atunci sigur e floare
        ok = 0                  #deci nu conteaza daca e treaza sau adormita pt ca o vom culege indiferent
        for i in scop:
            if i[0] == tip and i[1] >= 1:   #verificam daca trb sa mai culegem vreo floare in flor
                ok = 1                      #-> ajuta lower de mai sus ca sa ia si cazul cand floarea e adormita
        if ok == 0:
            return 0   #daca nu mai avem nev de floare de tipul resp, da return 0
        if mat[x][y] == tip.upper():  #daca floarea e adormita/ lit mare atunci nu mai trebuie verificata distanta
            return 1
        idx = 0
        for i in self.floriStatus:
            if i[0] == tip:
                break
            idx += 1
        minMan = rage[idx]   #rage[idx] = raza de acoperire la floarea resp
        for i in range(len(mat)):  #pt fiecare loc din matrice,
            for j in range(len(mat[0])): #distanta manhattan de la floarea resp de tip pana la pozitia pe care o verificam
                if mat[i][j] == tip:
                    man = abs(i - x) + abs(j - y)
                    if man <= minMan and man != 0:  #daca da vreuna mai putin decat raza + dist sa nu fie 0
                        return 0                    #pt ca vrem sa mutam pe pozitia unde e floarea si sa calc si distanta in aceeasi pozitie
        return 1                                     #daca nu da ret 0 atunci e ok si da ret 1

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []   #lista de succesori vida
        if nodCurent.lis == []:  #lista cu nodurile curente
            for i in range(len(self.scopuri)):  #parcurge lista cu bchetul scop
                nodCurent.lis.append([self.scopuri[i][0], 0]) # pune in nodCurent.lis literele florilor
        for lGol in range(len(nodCurent.info)): #(parcurge lista de liste -> matricea) luam pe rand fiecare linie lGol din matrice
            try:
                cGol = nodCurent.info[lGol].index('@') #in lista respectiva caut elem cu @ -> omuletul nostru(indicele pe linie e chiar coloana)
                break
            except:
                pass
        copieFlori = copy.deepcopy(nodCurent.floriStatus)
        copieMatrice = copy.deepcopy(nodCurent.info)
        for i in range(len(nodCurent.floriStatus)):     #verifica, pentru fiecare tip de floare, daca e treaza sau nu
            if copieFlori[i][1] != 0:
                copieFlori[i][1] -= 1
            elif copieFlori[i][2] != 0:
                copieFlori[i][2] -= 1
            else:
                copieFlori[i] = copy.deepcopy(self.floriStatus[i])
                flor = copieFlori[i][0]                                #dupa ce trece timpul de dormit, schimba literele din mare in mic
                for k in range(len(copieMatrice)):
                    for j in range(len(copieMatrice[0])):
                        if copieMatrice[k][j] == flor.upper():
                            copieMatrice[k][j] = flor.lower()
        # pus litere mari in loc de litere mici, daca copieFlori[i][1]==0 si copieFlori[i][2]!=0
        for i in copieFlori:   #daca floarea din floriStatus copie e egala cu floarea din matrice copie
            if i[1] == 0 and i[2] != 0:  #timp_treaza ajunge la 0 si timp_adormita e dif de zero
                for k in range(len(copieMatrice)):
                    for j in range(len(copieMatrice[0])):
                        if copieMatrice[k][j] == i[0]:
                            copieMatrice[k][j] = copieMatrice[k][j].upper()  #schimba lit mica cu litera mare => floare adormita
        nodCurent.info = copieMatrice
        #parcurge lista cu floriStatus si vede daca floarea e adormita sau nu
        #daca e adormita, atunci se uita in matrice si daca
        #floarea de pe poz respectiva corespunde cu floarea din lista cu status
        #daca corespunde, atunci schimba lit mica cu lit mare ca sa ararte ca floarea a adormit

        # stanga, dreapta, sus, jos
        linieMax = len(nodCurent.info)
        colMax = len(nodCurent.info)
        #coordonatele vecinilor practic
        directii = [[lGol, cGol - 1], [lGol, cGol + 1], [lGol - 1, cGol], [lGol + 1, cGol]]
        costCnt = 0
        for lPlacuta, cPlacuta in directii:
            if 0 <= lPlacuta < linieMax and 0 <= cPlacuta < colMax and self.checkPos(lPlacuta, cPlacuta,
                                                                                     nodCurent.rageFlori,
                                                                                     nodCurent.info, nodCurent.floriNr):
                copieMatrice = copy.deepcopy(nodCurent.info) #face o copie cu deep sa nu se modifice si in liste daca o modificam
                lista = copy.deepcopy(nodCurent.lis)
                copieMatrice[lGol][cGol] = '.'  #pun pe locul omuletului vecinul care e '.' -> e loc liber
                anteriorCulese = nodCurent.culese
                copieRageFlori = copy.deepcopy(nodCurent.rageFlori)
                copieFloriNr = copy.deepcopy(nodCurent.floriNr)

                if costCnt == 0 or costCnt == 1:
                    costArc = 1 + nodCurent.culese  #cost pt mutarea pe linie
                else:
                    costArc = 1 + nodCurent.culese // 2  #cost pt mutarea pe coloana
                if copieMatrice[lPlacuta][cPlacuta] == '.':
                    copieMatrice[lPlacuta][cPlacuta] = '@'  #si in locul unde era liber '.' pun omuletul daca era liber
                else:
                    tipFloare = copieMatrice[lPlacuta][cPlacuta].lower()  #flori treze in tipFloare
                    for i in range(len(nodCurent.floriNr)):
                        if copieFloriNr[i][0] == tipFloare: #daca gaseste un tip de floare din buchet care sa corespunda
                            copieFloriNr[i][1] -= 1         #cu floarea de pe poz vecina din matrice atunci scade nr de flori ramase de cules
                            break
                    copieMatrice[lPlacuta][cPlacuta] = '@' #dupa ce culege floarea, muta omuletul in locul ei
                    anteriorCulese += 1
                    costArc = 1  #cost intotdeauna 1 cand intra intr-o celula cu floare
                    for i in range(len(lista)):
                        if lista[i][0] == tipFloare:
                            lista[i][1] += 1
                    for i in range(len(nodCurent.floriStatus)):
                        if copieFlori[i][0] == tipFloare:
                            copieRageFlori[i] += 1

                if (not nodCurent.contineInDrum(
                        copieMatrice)) or anteriorCulese > nodCurent.culese:  # and not self.nuAreSolutii(copieMatrice):
                    # de adaugat costuri pe sus etc

                    listaSuccesori.append(  #daca nu e in drum, atunci il adaug in lista de succesori
                        NodParcurgere(copieMatrice, nodCurent, copieFlori, copieRageFlori, copieFloriNr, anteriorCulese,
                                      nodCurent.g + costArc,
                                      self.calculeaza_h(copieMatrice, tip_euristica, nodCurent.culese), lista))


        return listaSuccesori

    # euristica banala
    def calculeaza_h(self, infoNod, tip_euristica="euristica banala", cul=0):
        if tip_euristica == "euristica banala":
            return 1    #returnam 1(costul minim) pentru ca avem macar o mutare
        else:
            return self.total - cul #eur 1

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


def dfi(nodCurent, adancime, nrSolutiiCautate, max_noduri, total_noduri):
    # fout.write("Stiva actuala: " + "->".join(nodCurent.obtineDrum()))
    # input()
    current_time = time.time()
    if (round(current_time - t1) > timeout):
        fout.write("Timeout\n")
        return
    if adancime == 1 and gr.testeaza_scop(nodCurent):
        fout.write("Solutie: ")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        fout.write(f"{time.time() - t1}" + "secunde\n")
        fout.write(f"Maximul de noduri:{max_noduri}\n")
        fout.write(f'Totalul de noduri:{total_noduri}\n')
        fout.write("\n----------------\n")
        # input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    elif adancime > 1:
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        total_noduri += len(lSuccesori)
        max_noduri = max(max_noduri, len(lSuccesori))
        for sc in lSuccesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(sc, adancime - 1, nrSolutiiCautate, max_noduri, total_noduri)
    return nrSolutiiCautate


def depth_first_iterativ(gr, nrSolutiiCautate=1, max_noduri=-1, total_noduri=0):
    for i in range(1, 101):
        if nrSolutiiCautate == 0:
            return
        fout.write("**************\nAdancime maxima: " + f"{i}")
        nrSolutiiCautate = dfi(NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0,
                                             gr.calculeaza_h(gr.start)), i, nrSolutiiCautate, max_noduri, total_noduri)


def df(nodCurent, nrSolutiiCautate, max_noduri, total_noduri):
    if nrSolutiiCautate <= 0:  # testul acesta s-ar valida doar daca in apelul initial avem df(start,if nrSolutiiCautate=0)
        return nrSolutiiCautate
    # fout.write("Stiva actuala: " + "->".join(nodCurent.obtineDrum()))
    current_time = time.time()
    if (round(current_time - t1) > timeout):
        fout.write("Timeout\n")
        return
    if gr.testeaza_scop(nodCurent):
        fout.write("Solutie: ")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        fout.write(f"{time.time() - t1}" + "secunde\n")
        fout.write(f"Maximul de noduri:{max_noduri}\n")
        fout.write(f'Totalul de noduri:{total_noduri}\n')
        fout.write("\n----------------\n")
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    total_noduri += len(lSuccesori)
    max_noduri = max(max_noduri, len(lSuccesori))
    for sc in lSuccesori:
        if nrSolutiiCautate != 0:
            nrSolutiiCautate = df(sc, nrSolutiiCautate, max_noduri, total_noduri)

    return nrSolutiiCautate


def depth_first(gr, nrSolutiiCautate=1):
    # vom simula o stiva prin relatia de parinte a nodului curent
    max_noduri = -1
    total_noduri = 0
    df(NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0, gr.calculeaza_h(gr.start)),
       nrSolutiiCautate, max_noduri, total_noduri)


def breadth_first(gr, nrSolutiiCautate):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0,
                       gr.calculeaza_h(gr.start))]

    max_noduri = -1
    total_noduri = 0
    while len(c) > 0:
        # fout.write("Coada actuala: " + str(c))
        # input()
        nodCurent = c.pop(0)
        current_time = time.time()
        if (round(current_time - t1) > timeout):
            fout.write("Timeout\n")
            return
        if gr.testeaza_scop(nodCurent):
            fout.write("Solutie:")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            fout.write(f"{time.time() - t1}" + "secunde\n")
            fout.write(f"Maximul de noduri:{max_noduri}\n")
            fout.write(f'Totalul de noduri:{total_noduri}\n')
            fout.write("\n----------------\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent)

        total_noduri += len(lSuccesori)
        max_noduri = max(max_noduri, len(lSuccesori))
        c.extend(lSuccesori)


def a_star(gr, nrSolutiiCautate, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)

    c = [NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0,
                       gr.calculeaza_h(gr.start))]

    max_noduri = -1
    total_noduri = 0
    while len(c) > 0:

        nodCurent = c.pop(0)

        total_noduri += len(c)
        max_noduri = max(max_noduri, len(c))
        current_time = time.time()
        if (round(current_time - t1) > timeout):
            fout.write("Timeout\n")
            return
        if gr.testeaza_scop(nodCurent):
            fout.write("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            fout.write(f"{time.time() - t1}" + "secunde\n")
            fout.write(f"Maximul de noduri:{max_noduri}\n")
            fout.write(f'Totalul de noduri:{total_noduri}\n')
            fout.write("\n----------------\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break;
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_starOpt(gr, nrSolutiiCautate, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0,
                            gr.calculeaza_h(gr.start))]

    # l_open contine nodurile candidate pentru expandare (este echivalentul lui c din A* varianta neoptimizata)

    max_noduri = -1
    total_noduri = 0
    # l_closed contine nodurile expandate
    l_closed = []
    while len(l_open) > 0:
        # fout.write("Coada actuala: " + str(l_open))
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)
        total_noduri += len(l_open)
        max_noduri = max(max_noduri, len(l_open))
        current_time = time.time()
        if (round(current_time - t1) > timeout):
            fout.write("Timeout\n")
            return
        if gr.testeaza_scop(nodCurent):
            fout.write("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            fout.write(f"{time.time() - t1}" + "secunde\n")
            fout.write(f"Maximul de noduri:{max_noduri}\n")
            fout.write(f'Totalul de noduri:{total_noduri}\n')
            fout.write("\n----------------\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, tip_euristica, max_noduri, total_noduri):
    # fout.write("A ajuns la: ", nodCurent)
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f
    current_time = time.time()
    if (round(current_time - t1) > timeout):
        fout.write("Timeout\n")
        return 0, "gata"
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        fout.write("Solutie: ")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        fout.write(f"{time.time() - t1}" + "secunde\n")
        fout.write(f"Maximul de noduri:{max_noduri}\n")
        fout.write(f'Totalul de noduri:{total_noduri}\n')
        # fout.write(limita)
        fout.write("\n----------------\n")
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
    total_noduri += len(lSuccesori)
    max_noduri = max(max_noduri, len(lSuccesori))
    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, tip_euristica, max_noduri,
                                                  total_noduri)
        if rez == "gata":
            return 0, "gata"
        # fout.write("Compara ", rez, " cu ", minim)
        if rez < minim:
            minim = rez
        # fout.write("Noul minim: ", minim)
    return nrSolutiiCautate, minim


def ida_star(gr, nrSolutiiCautate, tip_euristica="euristica banala", max_noduri=-1, total_noduri=0):
    nodStart = NodParcurgere(gr.start, None, gr.floriStatus, gr.rageFlori, gr.scopuri, gr.culese, 0,
                             gr.calculeaza_h(gr.start))
    limita = nodStart.f

    while True:

        # fout.write("Limita de pornire: ", limita)
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, tip_euristica, max_noduri,
                                                  total_noduri)
        if rez == "gata":
            break
        if rez == float('inf'):
            fout.write("Nu mai exista solutii!")
            break
        limita = rez
    # fout.write(">>> Limita noua: ", limita)


gr = Graph("input_files/in4.txt")
fout = open("output_files/out4.txt", "w")
#gr = Graph("in1.txt")
#fout = open("out1.txt", "w")
if gr.noSol == 1:
    fout.write("Nu exista solutii")
    exit()
# Rezolvat cu breadth first
# print("Solutii obtinute cu breadth first:")
# breadth_first(gr, nrSolutiiCautate=3)

# print("\n\n##################\nSolutii obtinute cu UCS:")
# print("\nObservatie: stivele sunt afisate pe orizontala, cu baza la stanga si varful la dreapta.")
# uniform_cost(gr, nrSolutiiCautate=4)

timeout = 100
# Rezolvat cu breadth first
fout.write("Solutii obtinute cu breadth first:")
t1 = time.time()
breadth_first(gr, nrSolutiiCautate=1)

fout.write("Solutii obtinute cu depth first:")
t1 = time.time()
depth_first(gr, nrSolutiiCautate=1)

fout.write("Solutii obtinute cu depth first iterativ:")
t1 = time.time()
depth_first_iterativ(gr, nrSolutiiCautate=1)

fout.write("\n\n##################\nSolutii obtinute cu A*:")
t1 = time.time()
a_star(gr, nrSolutiiCautate=1, tip_euristica="euristica banala")
t1 = time.time()
a_star(gr, nrSolutiiCautate=1, tip_euristica="euristica 1")

fout.write("Solutii cu a_starOpt")
t1 = time.time()
a_starOpt(gr, nrSolutiiCautate=1, tip_euristica="euristica banala")
t1 = time.time()
a_starOpt(gr, nrSolutiiCautate=1, tip_euristica="euristica 1")

fout.write("Solutii cu ida_star")
t1 = time.time()
ida_star(gr, nrSolutiiCautate=1, tip_euristica="euristica banala")
t1 = time.time()
ida_star(gr, nrSolutiiCautate=1, tip_euristica="euristica 1")
