from rdflib import Graph, URIRef, RDF, Literal, Namespace
from rdflib.namespace import SKOS

ex = Namespace("http://example.org/")
g = Graph()

def create_node(counter, line):
    def extract_classmark(s):
        classmark = s.split(" ")[0]
        if classmark == "@":
            return None
        else:
            return classmark

    def extract_label(s):
        words = s.split()
        excluded_notation = " ".join(words[1:])
        return excluded_notation[2:]

    uri = ex[f"{counter}"]
    label = extract_label(line)
    if label:
        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, SKOS.prefLabel, Literal(label)))

    notation = extract_classmark(line)
    if notation:
        g.add((uri, SKOS.notation, Literal(notation)))


def extract_indentation(line):
    return int(line.split()[1][:2])


def identify_line(line):
    if line[0] != " ":
        return "new node"
    if line.strip()[0] == "*":
        return "new note"
    else:
        return "continued note"


def parse_source_file(file_path):
    with open(file_path, 'r') as file:
        counter = 0
        for line in file:
            line_type = identify_line(line)
            if line_type == "new node":
                create_node(counter, line)
                counter += 1


parse_source_file("source_code.txt")
print(g.serialize())
