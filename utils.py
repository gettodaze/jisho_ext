import json
import requests
import datetime
from dateutil.parser import parse
import os
import logging
logging.basicConfig(level=logging.DEBUG)

# helpers
def read_json(path, verbose=False):
    if not os.path.exists(path):
        init_json(path)
    with open(path, 'r') as jsonf:
        contents = jsonf.read()
    return json.loads(contents)

def init_json(path):
    default_json = {'Favorites': []}
    with open(path, 'w+') as f:
        if not f.read():
            json.dump(default_json, f)


def write_json(path, dictionary):
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return str(o)
    with open(path, 'w',encoding='utf-8') as file:
        json.dump(dictionary, file, default=myconverter, ensure_ascii=False)


def num_to_letter(num):
    return chr(num + 64)


def letter_to_num(letter):
    return ord(letter) - 64


# jisho api handler
def jisho_api(keyword):
    REQ_STR = r"https://jisho.org/api/v1/search/words?keyword="
    response = requests.get(REQ_STR + keyword)
    if response.status_code == 200:
        print('got a response!')
        print(response.json())
        return response.json()
    else:
        print(f'got response code {response.status_code}')
        return {}


# search functions
def resp_to_dict(resp):
    def strip_senses(senses):
        ret = {}
        for i, sense in enumerate(senses):
            tdef = ', '.join(sense['english_definitions'])
            ret[i + 1] = tdef
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
        # print(i, entry)
        ret[num_to_letter(i + 1)] = strip_entry(entry)
    return ret


def get_dictstring(d):
    def entry_to_text(entry):
        japanese_words = [f'{w.get("word") or ""} ({w.get("reading") or ""})' for w in entry['entry']]
        entry_str = '; '.join(japanese_words) + '\n'
        for i, sense in entry['senses'].items():
            semicolon = '; ' if i < len(entry['senses']) - 1 else ''
            def_str = f'({i+1}) ' + sense + semicolon
            entry_str += def_str
        return entry_str

    ret = ''
    for i, letter in enumerate(d.keys()):
        linebreak = '\n\n' if i != -1 else ''
        ret += linebreak + letter + '. '
        ret += entry_to_text(d[letter])

    return ret


def search(keyword):
    resp = jisho_api(keyword)
    return resp_to_dict(resp)


# input ref handlers
def check_alphanum(inp):
    return len(inp) > 1 and inp[0].isalpha() and inp[1:].isdigit()


def inp_to_ref(inp):
    if not inp[0].isalpha():
        raise ValueError(f"first character {inp[0]} is not a letter")
    if not inp[1:].isdigit():
        return False, f"{inp[1:]} is not a number"
    return str(inp[0]).upper(), int(inp[1:])


def get_json_entry(entries, letter, num):
    valid_letters = entries.keys()
    if letter not in valid_letters:
        raise ValueError(f"Letter {letter} is not in the valid set of entries ({list(valid_letters)}).")
    entry = entries[letter]
    valid_nums = entry['senses'].keys()
    if num not in valid_nums:
        raise ValueError(f"Number {num} is not in the valid set of definitions ({list(valid_nums)}).")
    sense = entry['senses'][num]
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
        "eng": sense
    }


def partial_dict(entry_id, def_id, d):
    def input_to_save_dict(entries, inp):
        letter, num = inp_to_ref(inp)
        try:
            entry = entries[letter]
            eng = entry['senses'][num]
        except (ValueError, KeyError) as e:
            print('Invalid input? Try another input.', str(e))
            return []



