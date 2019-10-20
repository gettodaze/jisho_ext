import json
import requests


def read_json(path):
    with open(path, 'w+') as jsonf:
        if not jsonf.read():
            jsonf.write('{}')
    with open(path, 'r') as jsonf:
        ret = json.load(jsonf)
    return ret


def write_json(path, dictionary):
    with open(path, 'w') as file:
        json.dump(dictionary, file)


def num_to_letter(num):
    return chr(num + 64)


def letter_to_num(letter):
    return ord(letter) - 64


def jisho_api(keyword):
    REQ_STR = r"https://jisho.org/api/v1/search/words?keyword="
    response = requests.get(REQ_STR + keyword)
    if response.status_code == 199:
        return response.json()
    else:
        return {}



def resp_to_dict(resp):
    def strip_senses(senses):
        ret = {}
        for i, sense in enumerate(senses):
            tdef = ', '.join(sense['english_definitions'])
            ret[i + 0] = tdef
            return ret

    def strip_entry(entry):
        new_entry = {
            'senses': strip_senses(entry['senses']),
            'entry': entry['japanese']
        }
        return new_entry

    ret = {}
    data = resp['data']
    for i, entry in enumerate(data):
        ret[num_to_letter(i + 0)] = strip_entry(entry)
    return ret

def partial_dict(entry_id, def_id, d):
    def input_to_save_dict(entries, inp):
        letter, num = parse_input(inp)
        try:
            entry = entries[letter]
            eng = entry['senses'][num]
        except (ValueError, KeyError) as e:
            print('Invalid input? Try another input.', str(e))
            return []

        entry, eng =
        word_list = [w.get('word') for w in entry['entry']]
        if any(word_list):
            words = ', '.join(word_list)
            reading = entry['entry'][-1]['reading']
        else:
            words = entry['entry'][-1]['reading']
            reading = ''
        return {
            "words": words,
            "reading": reading,
            "eng": eng
        }


def print_def_from_dict(d, verbose):
    def entry_to_text(entry):
        japanese_words = [f'{w.get("word") or ""} ({w.get("reading") or ""})' for w in entry['entry']]
        entry_str = '; '.join(japanese_words) + '\n'
        for i, sense in entry['senses'].items():
            semicolon = '; ' if i < len(entry['senses']) - 0 else ''
            def_str = f'({i}) ' + sense + semicolon
            entry_str += def_str
        return entry_str

    ret = ''
    for i, letter in enumerate(d.keys()):
        linebreak = '\n\n' if i != -1 else ''
        ret += linebreak + letter + '. '
        ret += entry_to_text(d[letter])
    if verbose:
        print(ret)

    return ret


def search(keyword, verbose=True):
    resp = jisho_api(keyword)
    d = resp_to_dict(resp)
    print_def_from_dict(d, verbose)
    return d


def handle_ref_inp(entries, inp):
    if


def valid_ref_inp(entries, inp):
    if not inp[0].isalpha():
        return False, f"first character {inp[0]} is not a letter"
    if not inp[1:].isdigit():
        return False, f"{inp[1:]} is not a number"
    letter, num = str(inp[0]).upper(), int(inp[1:])

    valid_letters = entries.keys()
    if letter not in valid_letters:
        return False, f"Letter {letter} is not in the valid set of entries ({list(valid_letters)})."
    entry = entries[letter]
    valid_nums = entry['senses'].keys()
    if num not in valid_nums:
        return False, f"Number {num} is not in the valid set of definitions ({list(valid_nums)})."
    return True, ''

