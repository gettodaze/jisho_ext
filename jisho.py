import utils
import datetime
import logging


class Jisho:
    def __init__(self, json_path=None, init_list=None):
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path or 'lists.json'
        self.lists = utils.read_json(self.json_path)
        self.cur_list = self.lists['.jj-default_list']
        if init_list:
            self.change_list(init_list)
        self.num_shown = 0
        self.handle_print('Welcome to John\'s Jisho.\nLoaded')


    def handle_input(self, inp):
        args = inp.split(maxsplit=1)
        first_arg, second_arg = args[0].upper(), args[1]
        if first_arg == '.Q':
            self.handle_print('Goodbye')
            return False
        elif first_arg == '.CL':
            self.change_list(second_arg)
        elif first_arg == '.NL':
            self.new_list(second_arg)
        elif first_arg == 'M':
            self.print_cur_word()
        elif inp.upper() == 'SL':
            self.show_list()
        elif inp.upper() == 'EL':
            self.export_list()
        elif utils.check_alphanum(inp):
            self.handle_save_code(inp)
        else:
            logging.info('Looking up: '+inp)
            self.lookup(inp)
        return True

    def get_lists(self):
        return list(k for k in self.lists.keys() if not k.startswith('.jj'))


    def change_list(self, to_list):
        if to_list in self.get_lists():
            self.cur_list = to_list
            logging.info("Changed list to "+to_list)
        else:
            logging.info("List "+to_list+" does not exist")

    def new_list(self, new_list):
        if new_list not in self.lists.keys():
            logging.info('Added ')
            self.lists[new_list] = []
            self.cur_list = new_list
            logging.info('Changing list to '+self.cur_list)
        else:
            logging.info(f'{new_list} already exists!')

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
        self.handle_print(toprint)

    def handle_print(self, lines):
        print(lines)


    def save_entry(self, inp):
        letter, num = utils.inp_to_ref(inp)
        selected = utils.get_json_entry(self.cur_word, letter, num)
        selected['timestamp'] = datetime.datetime.now()
        if any([selected['words'] == x['words'] for x in self.lists[self.cur_list]]):
            logging.info(f'{selected["words"]} already appears to be in {self.cur_list}')
        else:
            self.lists[self.cur_list].append(selected)
            utils.write_json(self.json_path, self.lists)
            logging.info(f'Saved to {self.cur_list}. {selected["words"]}:{selected["eng"]}.')


    def export_list(self, path=None):
        logging.info('Export list '+self.cur_list)
        path = path or 'export.txt'
        toline = lambda e: e['words'] + ':' + e['reading'] + '\n' + e['eng']
        cur_list_dict = self.lists[self.cur_list]
        with open(path, 'w+', encoding='utf-8') as outfile:
            content = '~'.join([toline(e) for e in cur_list_dict])
            print(content, file=outfile)

def main():
    logging.basicConfig(
        handlers=[logging.FileHandler('jisho.log', 'a+', 'utf-8')],
        level=logging.INFO)
    j = Jisho()
    'Welcome to Jisho.'
    cont = True
    while cont:
        inp = input('>>> ')
        cont = j.handle_input(inp)
    print('Goodbye')


if __name__ == '__main__':
    main()

