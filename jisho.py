import utils
import datetime
import logging


class Jisho:
    def __init__(self, json_path=None, init_list=None):
        self.handle_print(f'Welcome to John\'s Jisho. Type .h for help.', logging.debug)
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path or 'lists.json'
        self.lists = utils.read_json(self.json_path)
        self.cur_list = self.lists['.jj-default_list']
        if init_list:
            self.change_list(init_list)
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
            self.export_list()
        elif first_arg == '.SAL':
            self.handle_print('LISTS: ' + str(self.get_lists()))
        elif utils.check_alphanum(inp):
            self.handle_save_code(inp)
        else:
            self.lookup(inp)
        return True

    def get_lists(self):
        return list(k for k in self.lists.keys() if not k.startswith('.jj'))


    def change_list(self, to_list):
        if to_list in self.get_lists():
            self.cur_list = to_list
            self.handle_print("Changed list to "+to_list)
        else:
            self.handle_print("List "+to_list+" does not exist")

    def new_list(self, new_list):
        if not new_list:
            self.handle_print('You cannot have a list with a blank name')
            return
        if new_list not in self.get_lists():
            self.handle_print('Added '+new_list)
            self.lists[new_list] = []
            self.cur_list = new_list
            self.handle_print('Changing list to '+self.cur_list)
        else:
            self.handle_print(f'{new_list} already exists!')

    def show_list(self):
        logging.info('show list')
        print(self.cur_list+":")
        cur_list = self.lists[self.cur_list]
        for i, o in enumerate(reversed(cur_list)):
            entry_str = f'{i+1}. {o["words"]} {o["reading"]} {o["eng"]}'
            print(entry_str[:50])


    def handle_save_code(self, inp):
        logging.info('save code')
        self.save_entry(inp)

    def lookup(self, keyword):
        return_dict = utils.search(keyword)
        logging.debug(f'returned: {return_dict}')
        if return_dict:
            self.prev_dict = self.cur_word
            self.cur_word = return_dict
            self.print_cur_word()

    def print_cur_word(self):
        toprint = ''
        num_entries = len(self.cur_word)
        if self.num_shown >= num_entries:
            self.num_shown == 0
        if not num_entries:
            toprint += 'No word to print'
        else:
            show_low, show_high = self.num_shown + 1, min(num_entries, self.num_shown+3)
            toprint += f'Showing entries {show_low}-{show_high}/{num_entries}\n'
            print_str = utils.get_dictstring(self.cur_word, show_low-1, show_high)
            toprint += print_str + '\nPress m to show more.'
        self.handle_print(toprint, logging.debug)

    def handle_print(self, lines, logger=logging.info):
        print(lines)
        if logger:
            logger(lines)


    def save_entry(self, inp):
        letter, num = utils.inp_to_ref(inp)
        selected = utils.get_json_entry(self.cur_word, letter, num)
        selected['timestamp'] = datetime.datetime.now()
        if any([selected['words'] == x['words'] for x in self.lists[self.cur_list]]):
            self.handle_print(f'{selected["words"]} already appears to be in {self.cur_list}')
        else:
            self.lists[self.cur_list].append(selected)
            utils.write_json(self.json_path, self.lists)
            self.handle_print(f'Saved to {self.cur_list}. {selected["words"]}:{selected["eng"]}.')


    def export_list(self, path=None):
        self.handle_print('Export list '+self.cur_list)
        path = path or 'export.txt'
        toline = lambda e: e['words'] + ':' + e['reading'] + '\n' + e['eng']
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
        level=logging.INFO)
    j = Jisho()
    cont = True
    while cont:
        inp = input('>>> ')
        cont = j.handle_input(inp)


if __name__ == '__main__':
    main()

