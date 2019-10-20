import utils
import datetime

class Jisho:
    def __init__(self, json_path=None, cur_list=None):
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path or 'lists.json'
        self.lists = utils.read_json(self.json_path)
        self.cur_list = cur_list or list(self.lists.keys())[0]

    def handle_input(self, inp):
        is_alphanum = utils.check_alphanum(inp)
        if inp.upper() == 'CL':
            print('change list')
            self.change_list(inp)
        elif utils.check_alphanum(inp):
            print('save code')
            self.handle_save_code(inp)
        else:
            print('looking up: '+inp)
            self.lookup(inp)

    def change_list(self, inp):
        pass

    def handle_save_code(self, inp):
        self.save_entry(inp)

    def lookup(self, keyword):
        return_dict = utils.search(keyword)
        # print(f'returned: {return_dict}')
        if return_dict:
            self.prev_dict = self.cur_word
            self.cur_word = return_dict
            print(utils.get_dictstring(return_dict))

    def save_entry(self, inp):
        letter, num = utils.inp_to_ref(inp)
        selected = utils.get_json_entry(self.cur_word, letter, num)
        selected['timestamp'] = datetime.datetime.now()
        self.lists[self.cur_list].append(selected)
        utils.write_json(self.json_path, self.lists)
        print(f'Saved {inp}: {selected}')

    def write_csv_line(self, inp):
        line = utils.input_to_csv_line(self.cur_dict, inp)
        print(line)
        with open(self.csv_path, 'a+', encoding='utf-8') as outfile:
            outfile.write(line)

if __name__ == '__main__':
    j = Jisho()
    j.handle_input('watashi')
    j.handle_input('a1')