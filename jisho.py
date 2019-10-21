import utils
import datetime
import logging


class Jisho:
    def __init__(self, json_path=None, cur_list=None):
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path or 'lists.json'
        self.lists = utils.read_json(self.json_path)
        if cur_list:
            self.lists['.cur_lists'] = cur_list
        self.cur_list = self.lists['.cur_list']


    def handle_input(self, inp):
        is_alphanum = utils.check_alphanum(inp)
        if inp.upper() == 'Q':
            return False
        elif inp.upper() == 'CL':
            self.change_list()
        elif inp.upper() == 'NL':
            self.new_list()
        elif inp.upper() == 'SL':
            self.show_list()
        elif inp.upper() == 'EL':
            self.export_list()
        elif utils.check_alphanum(inp):
            self.handle_save_code(inp)
        else:
            logging.info('looking up: '+inp)
            self.lookup(inp)
        return True

    def change_list(self):
        logging.info('change list')
        all_lists = [k for k in self.lists.keys() if k[0] is not '.']
        inp = input(f'Please input list name from ({", ".join(all_lists)}): ')
        if inp in self.lists.keys():
            self.cur_list = inp
            self.lists['.cur_list'] = inp
            logging.info("Changed list to "+inp)
        else:
            logging.info("List "+inp+" does not exist")

    def new_list(self):
        logging.info('new list')
        inp = input('Please input new list name: ')
        if inp not in self.lists.keys():
            logging.info('Added ')
            self.lists[inp] = []
            self.cur_list = inp
            logging.info('Changing list to '+self.cur_list)
        else:
            logging.info(f'{inp} already exists!')

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
        num_entries = len(self.cur_word)
        if num_entries > 3:
            num_shown = 0
            cont = True
            while num_shown < num_entries and cont:
                show_low, show_high = num_shown + 1, min(num_entries, num_shown+3)
                num_shown = show_high
                print(f'Showing entries {show_low}-{show_high}/{num_entries}')
                print_str = utils.get_dictstring(self.cur_word, show_low-1, show_high)
                print(print_str)
                cont = input('Show more? [y/n]: ').upper() in ['Y', 'YES']


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


if __name__ == '__main__':
    j = Jisho()
    'Welcome to Jisho.'
    cont = True
    while cont:
        inp = input('>>> ')
        cont = j.handle_input(inp)
    print('Goodbye')
