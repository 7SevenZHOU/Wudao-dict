#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys


from src.CommandDraw import CommandDraw
from src.UserHistory import UserHistory
from src.WudaoClient import WudaoClient
from src.tools import is_alphabet


class WudaoCommand:
    def __init__(self):
        # Member
        self.word = ''
        self.param_list = []
        self.draw_conf = True
        self.is_zh = False
        # Init
        self.param_separate()
        self.painter = CommandDraw()
        self.history_manager = UserHistory()
        # client
        self.client = WudaoClient()

    # init parameters
    def param_separate(self):
        if len(sys.argv) == 1:
            self.param_list.append('h')
        else:
            for v in sys.argv[1:]:
                if v.startswith('-'):
                    self.param_list.append(v[1:])
                else:
                    self.word += ' ' + v
        self.word = self.word.strip()
        if self.word:
            if not is_alphabet(self.word[0]):
                self.is_zh = True

    # process parameters
    def param_parse(self):
        if len(self.param_list) == 0:
            return
        if 'h' in self.param_list or '-help' in self.param_list:
            print('Usage: wd [OPTION]... [WORD]')
            print('Youdao is wudao, An powerful dict.')
            print('-k, --kill                   kill the server process')
            print('-h, --help                   display this help and exit')
            print('-s, --short-desc             show description without the sentence')
            print('-o, --online-search          search word online')
            exit(0)
        # close server
        if 'k' in self.param_list or '-kill' in self.param_list:
            self.client.close()
            sys.exit(0)
        # short conf
        if 's' in self.param_list or '-short-desc' in self.param_list:
            self.draw_conf = False
        if not self.word:
            print('Usage: wdd [OPTION]... [WORD]')
            exit(0)

    # query word
    def query(self):
        # query on server
        server_context = self.client.get_word_info(self.word).strip()
        if server_context != 'None':
            wi = json.loads(server_context)
            if self.is_zh:
                self.painter.draw_zh_text(wi, self.draw_conf)
            else:
                self.history_manager.add_item(self.word)
                self.painter.draw_text(wi, self.draw_conf)
        else:
            # Online search
            if 'o' in self.param_list or '-online-search' in self.param_list:
                try:
                    from src.WudaoOnline import get_text, get_zh_text
                    from urllib.error import URLError
                    if self.is_zh:
                        word_info = get_zh_text(self.word)
                    else:
                        word_info = get_text(self.word)
                    if not word_info['paraphrase']:
                        print('No such word: %s found online' % self.word)
                        exit(0)
                    self.history_manager.add_item(self.word)
                    if not self.is_zh:
                        self.history_manager.add_word_info(word_info)
                        self.painter.draw_text(word_info, self.draw_conf)
                    else:
                        self.painter.draw_zh_text(word_info, self.draw_conf)
                except ImportError:
                    print('You need install bs4 first.')
                    print('Use \'pip3 install bs4\' or get bs4 online.')
                except URLError:
                    print('No Internet : Please check your connection first')
            else:
                # search in online cache first
                word_info = self.history_manager.get_word_info(self.word)
                if word_info:
                    self.history_manager.add_item(self.word)
                    self.painter.draw_text(word_info, self.draw_conf)
                else:
                    print('Error: no such word :' + self.word)
                    print('You can use -o to search online.')


def main():
    app = WudaoCommand()
    app.param_parse()
    app.query()


if __name__ == '__main__':
    main()
