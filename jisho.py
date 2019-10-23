import utils
import datetime
import logging
import os


class Jisho:
    _SETTINGS_PREF = '.jj-'
    _DEFAULT_LIST = _SETTINGS_PREF + 'default_list'
    _DISPLAY_NUM = _SETTINGS_PREF + 'display_num'
    _EXPORT_DIR = _SETTINGS_PREF + 'export_dir'

    default_json = {
        'Favorites': [],
        _DEFAULT_LIST: 'Favorites',
        _DISPLAY_NUM: 5,
        _EXPORT_DIR: 'jisho_exports'
    }
    def __init__(self, json_path=None):
        self.handle_print(f'Welcome to John\'s Jisho. Type .h for help.', logging.debug)
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path or 'lists.json'
        self.lists = utils.read_json(self.json_path)
        self.cur_list = self.lists[Jisho._DEFAULT_LIST]
        self.display_num = self.lists[Jisho._DISPLAY_NUM]
        self.num_shown = 0
        self.handle_print(f'Loaded {self.cur_list} from {self.json_path}.')


    def handle_input(self, inp):
        args = inp.split(maxsplit=1)
        if len(args) == 0:
            return True
        first_arg = args[0].upper()
        second_arg = args[1] if len(args) > 1 else ''
        if first_arg == '.Q':
            self.handle_print('Goodbye', logging.debug)
            return False
        if first_arg in ['.H', '.HELP']:
            self.handle_print(self.helpstring(), logging.debug)
        elif first_arg == '.CL':
            self.change_list(second_arg)
        elif first_arg == '.NL':
            self.new_list(second_arg)
        elif first_arg == 'M':
            self.print_cur_word()
        elif first_arg == '.SL':
            self.show_list()
        elif first_arg == '.EL':
            self.export_list(second_arg)
        elif first_arg == '.SAL':
            self.handle_print('LISTS: ' + str(self.get_lists()))
        elif first_arg == '.NUM':
            self.change_display_num(second_arg)
        elif first_arg == '.ED':
            self.change_export_directory(second_arg)
        elif first_arg == '.S':
            self.save()
        elif first_arg in ['.AN']:
            args = inp.split(maxsplit=2)
            if len(args) != 3:
                self.handle_print('Improper number of arguments. Usage .AN <num> <note>, where num is from this list:')
                self.show_list()
            else:
                self.add_note(args[1], args[2])
        elif utils.check_alphanum(first_arg):
            self.handle_save_code(first_arg, second_arg)
        else:
            self.lookup(inp)
        return True

    def get_lists(self):
        return list(k for k in self.lists.keys() if not k.startswith('.jj'))


    def change_list(self, to_list):
        if to_list in self.get_lists():
            self.cur_list = to_list
            self.lists[Jisho._DEFAULT_LIST] = to_list
            self.handle_print("Changed list to "+to_list)
        else:
            self.handle_print("List "+to_list+" does not exist")

    def change_display_num(self, disp_num_str):
        logging.info('Changing display num to '+disp_num_str)
        if not disp_num_str.isdecimal() or int(disp_num_str) < 1:
            self.handle_print(f'"{disp_num_str}" is not a valid number of entries to print.')
        else:
            disp_num = int(disp_num_str)
            self.lists[Jisho._DISPLAY_NUM] = disp_num
            self.display_num = disp_num
            self.handle_print(f'Changed number of entries to display to {disp_num}')

    def change_export_directory(self, dir_name):
        if not os.path.isdir(dir_name):
            try: 
                os.mkdir(dir_name)
            except OSError as e:
                self.handle_print('Invalid Directory '+dir_name)
                return
            self.lists[Jisho._EXPORT_DIR] = dir_name




    def new_list(self, new_list):
        if not new_list:
            self.handle_print('You cannot have a list with a blank name')
        elif new_list not in self.get_lists():
            self.handle_print('Added '+new_list)
            self.lists[new_list] = []
            self.cur_list = new_list
            self.handle_print('Changing list to '+self.cur_list)
        else:
            self.handle_print(f'{new_list} already exists!')

    def show_list(self):
        logging.info('show list')
        paragraph = self.cur_list+":\n"
        cur_list = self.lists[self.cur_list]
        get_first = lambda x: x.split(',')[0]
        for i, o in enumerate(cur_list):
            entry_str = f'{i+1}. {get_first(o["words"])} {get_first(o["reading"])} {get_first(o["eng"])}.'
            note = f' Note: {o["note"]}' if o['note'] else ''
            printline = entry_str + note
            paragraph += printline + '\n'
        self.handle_print(paragraph)

    def add_note(self, num, note):
        logging.info('entered add note')
        if not num.isdecimal():
            self.handle_print(f"'{num}' is not a decimal.")
            return

        cur_list = self.lists[self.cur_list]
        i = int(num) - 1
        if i not in range(len(cur_list)):
            self.handle_print('Invalid number.')
        else:
            cur_list[i]['note'] = note
            self.save()


    def handle_save_code(self, code, note):
        logging.info('save code')
        self.save_entry(code, note)

    def lookup(self, keyword):
        return_dict = utils.search(keyword)
        logging.debug(f'returned: {return_dict}')
        if return_dict:
            self.prev_dict = self.cur_word
            self.cur_word = return_dict
            self.num_shown = 0
            self.handle_print('\n'*5+keyword)
            self.print_cur_word()

    def print_cur_word(self):

        toprint = ''
        num_entries = len(self.cur_word)
        logging.debug(f'num entries: {num_entries}. num shown: {self.num_shown}.')
        if self.num_shown >= num_entries:
            self.num_shown = 0
            logging.debug(f'reset num_shown to {self.num_shown}')
        if not num_entries:
            toprint += 'No word to print'
        else:
            show_low, show_high = self.num_shown + 1, min(num_entries, self.num_shown+self.display_num)
            toprint += f'Showing entries {show_low}-{show_high}/{num_entries}\n'
            print_str = utils.get_dictstring(self.cur_word, show_low-1, show_high)
            show_more = '\nPress m to show more\n' if show_high < num_entries else ''
            toprint += print_str + show_more
            self.num_shown = show_high
        self.handle_print(toprint, logging.debug)

    def handle_print(self, lines, logger=logging.info):
        print(lines)
        if logger:
            logger(lines.strip())


    def save_entry(self, inp, note):
        letter, num = utils.inp_to_ref(inp)
        try:
            selected = utils.get_json_entry(self.cur_word, letter, num)
        except ValueError as e:
            self.handle_print(e)
            return
        selected['timestamp'] = datetime.datetime.now()
        selected['note'] = note
        if any([selected['words'] == x['words'] for x in self.lists[self.cur_list]]):
            self.handle_print(f'{selected["words"]} already appears to be in {self.cur_list}')
        else:
            self.lists[self.cur_list].append(selected)
            self.save()
            self.handle_print(f'Saved to {self.cur_list}. {selected["words"]}:{selected["eng"]}.')


    def save(self):
        utils.write_json(self.json_path, self.lists)

    def export_list(self, path=None):
        def toline(e):
            words, reading, eng, note = e['words'], e['reading'], e['eng'], e['note']
            main = f'{words}:{reading}\n{eng}'
            note = f' ({note})' if note else ''
            return main + note

        self.handle_print('Export list '+self.cur_list)
        if not path:
            folder = 'exports'
            if not os.path.exists('exports'):
                os.makedirs('exports')
        path = '{self.cur_list}_jisho_export.txt'
        cur_list_dict = self.lists[self.cur_list]
        with open(path, 'w+', encoding='utf-8') as outfile:
            content = '~'.join([toline(e) for e in cur_list_dict])
            print(content, file=outfile)
    
    def helpstring(self):
        return f"""John's Jisho.
Current list: {self.cur_list}
Current json: {self.json_path}
Type in a keyword or a special argument. Arguments
Q: quit
.H: helpstring
.CL <list>: change list to <list>
.NL <list>: create new list <list>
.SL: show current list
.EL: export list
M: more definitions
letter+number combo: save word-sense pair to list."""

def main():
    logging.basicConfig(
        handlers=[logging.FileHandler('jisho.log', 'a+', 'utf-8')],
        level=logging.DEBUG)
    j = Jisho()
    cont = True
    while cont:
        inp = input(f'[{j.cur_list}]> ')
        cont = j.handle_input(inp)


if __name__ == '__main__':
    main()

