from copy import deepcopy


class KONWXML:

    def __init__(self, root):
        self._root = root

    def _replace_text(self, d):
        for elem in self._root.iter():
            te = elem.text
            if te is None:
                continue
            spos = 0
            # znajdz zmienne w linii
            zmset = []
            while True:
                beg = te.find("{{", spos)
                end = te.find("}}", spos)
                if beg >= 0 and end > 0:
                    varia = te[beg+2:end]
                    if varia in d:
                        zmset.append(varia)
                else:
                    break
                spos = end+2

            # teraz zamien
            for zm in zmset:
                subst = "{{" + zm + "}}"
                print(zm, d[zm])
                te = te.replace(subst, d[zm])

            elem.text = te

    def _replace_all(self, prefix, d, alista):
        self._replace_text(d)

    def _replace_linie(self, d, alista, plist, klista):
        root = self._root
        taglist = "{{LINIE" + plist + "}}"
        lte = None
        notable = 0
        # tutaj wyszukuj odpowiedniej tabeli oznaczone {{LINIE...}}
        # jest to koślawe, najpierw znajduje tag i zakłada,
        # że nastepny table jest tym szukanym
        for elem in root.iter():
            te = elem.text
            if elem.tag == "table":
                notable += 1
            if te is None:
                continue
            if te == taglist:
                lte = elem
                break
        if lte is None:
            return
        # usuwa znacznik
        elem = root.find(f'.//p[.="{taglist}"]')
        parent = root.find(f'.//p[.="{taglist}"]/..')
        parent.remove(elem)

        # teraz szuka table o właściwym numerz
        tablepar = root.findall(".//table")[notable]
        # tutaj ./, tylko direct children
        trlist = tablepar.findall("./tr")
        # rozpoznanie, który element jest iterowalny
        tr = trlist[0] if len(trlist) == 1 else trlist[1]
        insert = -1 if len(trlist) <= 2 else 1
        # usun iterowalny element (i potem będzie powielny w pętli)
        lista = alista.get(klista)
        if lista is None:
            for t in trlist:
                tablepar.remove(t)
            return
        tablepar.remove(tr)
        it = iter(lista) if insert == -1 else reversed(lista)
        for e in it:
            trc = deepcopy(tr)
            # _replace_text(trc, e)
            # tutaj rekurencyjnie podmnieniaj zawartość tabeli
            self._replace_all(trc, plist, d | e, e)
            if insert == -1:
                tablepar.append(trc)
            else:
                tablepar.insert(insert, trc)
