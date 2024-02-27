from rdflib import Graph, RDF, Literal, Namespace
from rdflib.namespace import SKOS

ex = Namespace("http://example.org/")
g = Graph()


def create_node(uri, lines):

    this_line = lines[0]
    g.add((uri, RDF.type, SKOS.Concept))

    def extract_classmark(s):
        classmark = s.split(" ")[0]
        if classmark == "@":
            return None
        else:
            return classmark

    def extract_labels(lines):

        def add_to_label(label, new_line):

            def remove_excess_whitespace(string):
                words = string.split()
                return " ".join(words)

            label += f" {remove_excess_whitespace(new_line)}"
            return label

        first_line_words = this_line.split()
        label_string = " ".join(first_line_words[1:])[2:]
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

        return label_string.split(", ")

    labels = extract_labels(lines)
    for i in range(len(labels)):
        if i == 0:
            pred = SKOS.prefLabel
        else:
            pred = SKOS.altLabel
        g.add((uri, pred, Literal(labels[i])))
    notation = extract_classmark(this_line)
    if notation:
        g.add((uri, SKOS.notation, Literal(notation)))


def extract_indentation(line):
    return int(line.split()[1][:2])


def identify_line(line): #some nodes start with without @ sign
    if line[0] != " ":
        return "new node"
    if line.strip()[0] == "*":
        return "new note"
    else:
        return "continued"


def parse_source_file(file_path):
    with open(file_path, 'r') as file:
        counter = 1
        lines = file.readlines()
        for i in range(len(lines)):
            line_type = identify_line(lines[i])
            if line_type == "new node":
                uri = ex[f"{str(counter).zfill(4)}"]
                create_node(uri, lines[i:])
                counter += 1


parse_source_file("source_code.txt")
g.serialize(destination="tbl.ttl")
print(g.serialize())
