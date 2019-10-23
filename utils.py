import json
import requests
import datetime
from dateutil.parser import parse
import os
import logging
from jisho import Jisho


# helpers
def read_json(path):
    if not os.path.exists(path):
        logging.info('No file found at '+path)
        init_json(path)
    with open(path, 'r', encoding='utf-8') as jsonf:
        contents = jsonf.read()
    try:
        logging.info('Loading from '+path)
        ret = json.loads(contents)#, encoding='utf-8')
    except json.decoder.JSONDecodeError:
        logging.error(f'The save file {path} is not in proper JSON form. \
        Please delete the file or choose a different file, or you will not be able to save data.')
        ret = {}
    return ret


def init_json(path):
    logging.info('Creating file at '+path)
    default_json = Jisho.default_json
    with open(path, 'w+') as f:
        if not f.read():
            json.dump(default_json, f)


def write_json(path, dictionary):
    logging.info(f'Writing to '+path)
    logging.debug(f'dict: '+ repr(dictionary))
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return str(o)
    with open(path, 'w',encoding='utf-8') as file:
        json.dump(dictionary, file, default=myconverter, ensure_ascii=False, indent=4)


def num_to_letter(num):
    return chr(num + 64)


def letter_to_num(letter):
    return ord(letter) - 64


# jisho api handler
def jisho_api(keyword):
    REQ_STR = r"https://jisho.org/api/v1/search/words?keyword="
    response = requests.get(REQ_STR + keyword)
    if response.status_code == 200:
        logging.info('got a response!')
        #logging.info(response.json())
        return response.json()
    else:
        logging.info(f'got response code {response.status_code}')
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
        ret[num_to_letter(i + 1)] = strip_entry(entry)
    return ret


def get_dictstring(d, start=None, end=None):
    def entry_to_text(entry):
        japanese_words = [f'{w.get("word") or ""} ({w.get("reading") or ""})' for w in entry['entry']]
        entry_str = '; '.join(japanese_words) + '\n'
        for n, sense in entry['senses'].items():
            semicolon = '; ' if i < len(entry['senses']) - 1 else ''
            def_str = f'({n}) ' + sense + semicolon
            entry_str += def_str
        return entry_str
    if start is None or start >= len(d) or start < 0:
        start = 0
    if end is None or end > len(d) or end < 0:
        end = len(d)
    ret = ''
    keys = list(d.keys())
    for i in range(start, end):
        letter = keys[i]
        linebreak = '' if i == start else '\n\n'
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
    logging.debug(f'get_json_entry: {letter}{num}')
    valid_letters = entries.keys()
    if letter not in valid_letters:
        raise ValueError(f"Letter {letter} is not in the valid set of entries ({list(valid_letters)}).")
    entry = entries[letter]
    logging.debug(f'{letter} is valid! Refers to entry {entry} ')
    valid_nums = entry['senses'].keys()
    if num not in valid_nums:
        raise ValueError(f"Number {num} is not in the valid set of definitions ({list(valid_nums)}).")
    sense = entry['senses'][num]
    logging.debug(f'{num} is valid! Refers to sense {sense}')
    word_list = set([w['word'] for w in entry['entry'] if w.get('word')])
    reading_list = set(w['reading'] for w in entry['entry'] if w.get('reading'))
    if word_list:
        words = ', '.join(word_list)
        reading = ', '.join(reading_list)
    else:
        words = ', '.join(reading_list) or ''
        reading = ''
    ret = {
        "words": words,
        "reading": reading,
        "eng": sense
    }
    logging.debug(f'get_json_entry to return {ret}')
    return ret


def partial_dict(entry_id, def_id, d):
    def input_to_save_dict(entries, inp):
        letter, num = inp_to_ref(inp)
        try:
            entry = entries[letter]
            eng = entry['senses'][num]
        except (ValueError, KeyError) as e:
            logging.error('Invalid input? Try another input.')
            return []



