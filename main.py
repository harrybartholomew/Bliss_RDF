from rdflib import Graph, RDF, Literal, Namespace
from rdflib.namespace import SKOS

ex = Namespace("http://example.org")
bliss = Namespace("http://example.org/bliss#")
g = Graph()


def create_node(uri, lines):
    this_line = lines[0]

    def remove_excess_whitespace(string):
        words = string.split()
        return " ".join(words)

    # Concept
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.inScheme, ex[""]))

    # Notation
    def extract_classmark(s):
        classmark = s.split(" ")[0]
        if classmark == "@":
            return None
        else:
            return classmark

    notation = extract_classmark(this_line)
    if notation:
        g.add((uri, SKOS.notation, Literal(notation)))

    # Labels
    def extract_labels(lines):

        def remove_surrounding_brackets(string):  # still need to deal with these
            brackets = ["(", "<", "[", "{", ")", ">", "]", "}"]
            while string[0] in brackets and string[-1] in brackets:
                string = string[1:-1]
            return string

        def add_to_label(label, new_line):

            label += f" {remove_excess_whitespace(new_line)}"
            return label

        first_line_words = this_line.split()
        label_string = remove_excess_whitespace(" ".join(first_line_words[1:])[2:])
        if label_string[0] == "*":
            return []
        more_labels = True
        lines_ahead = 1
        while more_labels:
            if len(lines) > 1:
                next_line = lines[lines_ahead]
                if identify_line(next_line) == "continued":
                    label_string = add_to_label(label_string, next_line)
                    lines_ahead += 1
                else:
                    more_labels = False
            else:
                more_labels = False

        labels = remove_surrounding_brackets(label_string).split(", ")
        bracketless_labels = []
        for label in labels:
            bracketless_labels.append(remove_surrounding_brackets(label))
        return bracketless_labels

    labels = extract_labels(lines)
    for i in range(len(labels)):
        if i == 0:
            pred = SKOS.prefLabel
        else:
            pred = SKOS.altLabel
        g.add((uri, pred, Literal(labels[i], lang="en")))

    # Notes
    def create_notes(lines):

        notes = []
        lines_ahead = 1

        def check_first_line_note(line):
            is_note = this_line.find("*")
            if is_note == -1:
                return False
            else:
                return line[is_note:]

        def new_note(note, lines_ahead):
            note_continues = True
            note = remove_excess_whitespace(note)
            lines_ahead += 1
            while note_continues:
                if len(lines) > lines_ahead:
                    next_line = lines[lines_ahead]
                    if identify_line(next_line) == "continued":
                        note = add_to_note(note, next_line)
                        lines_ahead += 1
                    else:
                        g.add((uri, SKOS.note, Literal(note, lang="en")))
                        return lines_ahead
                else:
                    g.add((uri, SKOS.note, Literal(note, lang="en")))
                    return lines_ahead

        def add_to_note(note, new_line):
            note += f" {remove_excess_whitespace(new_line)}"
            return note

        first_note = check_first_line_note(this_line)
        if first_note:
            lines_ahead = new_note(first_note, lines_ahead)
        more_notes = True
        while more_notes:
            if len(lines) > lines_ahead:
                if identify_line(lines[lines_ahead]) == "new note":
                    lines_ahead = new_note(lines[lines_ahead], lines_ahead)
                else:
                    more_notes = False
            else:
                more_notes = False

    create_notes(lines)


def create_hierarchy(hierarchy, uri, line):
    def extract_indentation(line):
        return int(line.split()[1][:2])

    indentation = extract_indentation(line)
    hierarchy[indentation] = uri
    if indentation == 1:
        g.add((uri, SKOS.topConceptOf, ex[""]))
    else:
        broader_uri = hierarchy[indentation - 1]
        g.add((uri, SKOS.broader, broader_uri))
    return hierarchy


def identify_line(line):  # some nodes start with without @ sign
    if line[0] != " ":
        return "new node"
    if line.strip()[0] == "*":
        return "new note"
    else:
        return "continued"


def parse_source_file(file_path):
    with open(file_path, 'r') as file:
        g.add((ex[""], RDF.type, SKOS.ConceptScheme))
        counter = 1
        lines = file.readlines()
        hierarchy = {0: "root"}
        for i in range(len(lines)):
            line_type = identify_line(lines[i])
            if line_type == "new node":
                uri = ex[f"/{str(counter).zfill(4)}"]
                create_node(uri, lines[i:])
                counter += 1
                hierarchy = create_hierarchy(hierarchy, uri, lines[i])


parse_source_file("source_code.txt")
g.serialize(destination="tbl.ttl")
