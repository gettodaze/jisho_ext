import utils

class Jisho:
    def __init__(self, json_path, cur_list=None):
        self.cur_word = {}
        self.prev_word = {}
        self.json_path = json_path
        self.lists = read_json(self.json_path)
        self.cur_list = cur_list

    def lookup(self, keyword):
        self.prev_dict = self.cur_word
        self.cur_word = search(keyword)

    def save_entry(self, inp):
        selected = input_to_dict(cur_list, inp)
        self.selected[timestamp] = datetime.datetime.now()
        self.lists[self.cur_list].append(selected)
        write_json(self.json_path, self.lists)

    def write_csv_line(self, inp):
        line = input_to_csv_line(self.cur_dict, inp)
        print(line)
        with open(self.csv_path, 'a+', encoding='utf-8') as outfile:
            outfile.write(line)