from typing import Collection, Set, List, Dict, Tuple

UM_LINE_TEMPLATE = "%s\t%s\t%s\n"


class UmLine:
    """
    Класс, представляющий одну строку формата UniMorph
    """
    form: str
    lemma: str
    grammar: List[str]

    def __init__(self, form: str, lemma: str, grammar: List[str]):
        self.form = form
        self.lemma = lemma
        self.grammar = grammar

    @property
    def str_grammar(self) -> str:
        return ",".join(self.grammar)

    @staticmethod
    def from_ud(line: str) -> "UmLine":
        line = line.split("\t")
        grammar = line[5].split(";")
        um = UmLine(line[1], line[2], grammar)
        um._preclean_ud_grammar()
        return um

    @staticmethod
    def from_um(line: str) -> "UmLine":
        line = line.strip("\n").split("\t")
        grammar = line[2].split(";")
        return UmLine(line[1].strip("\""), line[0].strip("\""), grammar)

    def clean_grammar(self) -> None:
        """
        после автоматических обработок
        """
        if type(self.grammar) != list:
            return
        if "V.PTCP" in self.grammar:

            self.grammar[0] = "V"
            if len(self.grammar) < 3:
                self.grammar.append("PRS")
            else:
                self.grammar[2] = "PRS"
            if self.form.endswith("ים"):
                self.grammar.append("MASC")
            elif self.form.endswith("ות"):
                self.grammar.append("FEM")
            elif self.form.endswith("ת") \
                    and not self.lemma.endswith("ת") \
                    or self.form.endswith("תת"):
                self.grammar.append("FEM")
            elif self.form.endswith("ה") and not self.lemma.endswith("ה"):
                self.grammar.append("FEM")
            else:
                self.grammar.append("MASC")

    def _preclean_ud_grammar(self) -> None:
        if type(self.grammar) != list:
            return
        if "{1/2/3}" in self.grammar:
            self.grammar.remove("{1/2/3}")
        if "{DU/PL}" in self.grammar:
            i = self.grammar.index("{DU/PL}")
            self.grammar[i] = "PL"
        if "{PL/SG}" in self.grammar:
            i = self.grammar.index("{PL/SG}")
            self.grammar[i] = "PL" if self.form.endswith("ים") else "SG"

    def __hash__(self) -> int:
        return hash(self.form) + hash(self.lemma) + hash(tuple(self.grammar))

    def __eq__(self, other: object) -> bool:
        if other.__class__ != UmLine:
            return False
        return self.form == other.form \
            and self.lemma == other.lemma \
            and self.grammar == other.grammar


class PseudoUmLine(UmLine):
    """
    Класс, также представляющий одну строку из UniMorph,
    с переопределенными методами __hash__ и __eq__,
    чтобы при добавлении сущности в set сохранялись сущности
    с разными грамматическими значениями
    с целью выявления различий между автоматической конвертацией
    из UD и оригинальными файлами
    """
    def __init__(self, form: str, lemma: str, grammar: Set[str]):
        self.form = form
        self.lemma = lemma
        self.grammar = grammar

    @staticmethod
    def from_ud(line: str) -> "PseudoUmLine":
        um = super().from_ud(line)
        return PseudoUmLine(um.form, um.lemma, set(um.grammar))

    @staticmethod
    def from_um(line: str) -> "PseudoUmLine":
        um = super().from_um(line)
        return PseudoUmLine(um.form, um.lemma, set(um.grammar))

    def __hash__(self) -> int:
        _hash = 0
        for g in self.grammar:
            _hash += hash(g)
        return _hash

    def __eq__(self, other: object) -> bool:
        if other.__class__ != PseudoUmLine:
            return False
        return self.grammar == other.grammar


def create_um_file(name: str, entities: Collection[UmLine]) -> None:
    with open(name, "w", encoding="utf-8") as f:
        for e in entities:
            grammar = ";".join(e.grammar)
            f.write(UM_LINE_TEMPLATE % (e.lemma, e.form, grammar))


def is_verb_prs_sg(grammar: Collection[str]):
    return "V" in grammar and "PRS" in grammar and "SG" in grammar


def extend_lamed_hei_verbs(entities: List[UmLine]) -> None:
    """
    for sorted collection
    """
    new_entities = []
    for i in range(len(entities)):
        if entities[i].lemma.endswith("ה") and is_verb_prs_sg(entities[i].grammar):
            verbs = []
            for j in range(max(0, i - 20), min(i + 20, len(entities))):
                if entities[j].form == entities[i].form and is_verb_prs_sg(entities[j].grammar):
                    verbs.append(entities[j])
            if len(verbs) == 1:
                if "FEM" in verbs[0].grammar:
                    k = verbs[0].grammar.index("FEM")
                    verbs[0].grammar[k] = "MASC"
                    new_entities.append(verbs[0])
                elif "MASC" in verbs[0].grammar:
                    k = verbs[0].grammar.index("MASC")
                    verbs[0].grammar[k] = "FEM"
                    new_entities.append(verbs[0])
    entities.extend(new_entities)
