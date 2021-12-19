import string

from um_utils import PseudoUmLine, create_um_file, UmLine, extend_lamed_hei_verbs


def step1():
    """
    Первичная обработка изначальных данных,
    создание списков с различной грамматикой, которая есть,
    просто посмотреть, с чем вообще работать придется
    """
    converted_ud_grammar = set()
    full_ud_grammar = []
    um_grammar = set()
    incorrect_ud = set()

    with open("heb_um.conllu", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if not line.startswith("#") and not line.isspace():
            converted = UmLine.from_ud(line)
            if converted.form not in string.punctuation:
                full_ud_grammar.append(UmLine.from_ud(line))
            converted_ud_grammar.add(PseudoUmLine.from_ud(line))

    with open("heb", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        um_grammar.add(PseudoUmLine.from_um(line))

    for g in converted_ud_grammar:
        if g in um_grammar:
            um_grammar.remove(g)
        else:
            incorrect_ud.add(g)

    create_um_file("g_um", um_grammar)
    create_um_file("g_ud", incorrect_ud)
    create_um_file("g_ud_full", full_ud_grammar)


def step2():
    all_entities = set()

    with open("new_final.txt", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if "_" in line or "NUM" in line or "PROPN" in line:
            continue
        um_line = UmLine.from_um(line)
        um_line.clean_grammar()
        all_entities.add(um_line)

    with open("heb", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        all_entities.add(UmLine.from_um(line))

    all_entities = list(all_entities)
    all_entities.sort(key=lambda um: (um.lemma, um.form))
    extend_lamed_hei_verbs(all_entities)
    all_entities.sort(key=lambda um: (um.lemma, um.form))
    create_um_file("done2", all_entities)


step2()
