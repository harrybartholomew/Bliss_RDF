import re


def find_indentation(input_string):
    match = re.search(r'\s(\d+)[^\d\s]', input_string)
    if match:
        return int(match.group(1))
    else:
        return None


def extract_label(input_string, indentation):
    indentation_string = str(indentation)
    if len(indentation_string) == 1:
        indentation_string = "0" + indentation_string
    indentation_index = input_string.find(indentation_string)
    if indentation_index != -1:
        label = input_string[indentation_index + 2:]
        return label
    return None


def parse_source_file(file_path):
    with open(file_path, 'r') as file:
        indentation = 0
        notation = ""
        label = ""
        note = None
        notes = []
        for line in file:
            if line[0] != " ":
                if note is not None:
                    notes.append(note)
                print(f"\n{'=' * indentation}{notation} - {label}{' ' * indentation}")
                for note in notes:
                    print(f"{' ' * indentation}{note}")
                notes = []
                note = None
                notation = line.split(" ")[0]
                indentation = find_indentation(line)
                label = extract_label(line, indentation)
            else:
                if line.strip()[0] == "*":
                    if note is not None:
                        notes.append(note)
                    note = line.strip()
                else:
                    note += f" {line.strip()}"



parse_source_file("source_code.txt")
