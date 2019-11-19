import pandas as pd
from pyknp import KNP

class SentimentAnalysis():
    def __init__(self,dic):
        self.dic = dic

    def OrganizeInfo(self,fstring):
        #形態素解析の結果をword_info = ["正規化表現","品詞","否定表現"]の形にする

        self.word_info = []
        self.begin = fstring.find('正規化代表表記:')
        self.end = fstring.find('/', self.begin + 1)
        self.word_info.append(fstring[self.begin + len('正規化代表表記:') : self.end])

        if '体言' in fstring:
            self.word_info.append('名詞')
            self.word_info.append(0)
        elif '用言:形' in fstring:
            self.word_info.append('形容詞')
            if '否定表現' in fstring:
                self.word_info.append(-1)
            else:
                self.word_info.append(1)
        elif '用言:動' in fstring:
            self.word_info.append('動詞')
            self.word_info.append(0)
        elif '副詞' in fstring:
            self.word_info.append('副詞')
            self.word_info.append(0)
        else:
            self.word_info.append('')
            self.word_info.append(0)

        return self.word_info


    def select_dependency_structure(self,knp,line):
        #係り受け構造を抽出
        # 解析
        self.result = knp.parse(line)
        # 文節リスト
        self.bnst_list = self.result.bnst_list()
        # 文節リストをidによるディクショナリ化する
        self.bnst_dic = dict((x.bnst_id, x) for x in self.bnst_list)

        self.tuples = []
        for bnst in self.bnst_list:
            if bnst.parent_id != -1:
                self.tuples.append((self.OrganizeInfo(bnst.fstring),self.OrganizeInfo(self.bnst_dic[bnst.parent_id].fstring)))

        for t in self.tuples:
            if t[0][1]=='形容詞' and t[1][1]=='形容詞':
                self.tuples.remove(t)
            elif t[0][1]=='副詞' and t[1][1]=='副詞':
                self.tuples.remove(t)

        return self.tuples

    def calcScore(self,tuples):
        #first => second
        self.scores = {}
        self.score = 0
        for t in tuples:
            self.first = t[0]
            self.second = t[1]
            self.reverse = 0
            ##名詞-形容詞ペアのスコア計算
            if (self.second[1]=='形容詞' and self.first[1]=='名詞') or (self.first[1]=='形容詞' and self.second[1]=='名詞'):
                if self.second[1]=='形容詞':
                    self.keiyousi = self.second[0]
                    self.reverse = self.second[2]
                    self.meisi = self.first[0]
                else:
                    self.keiyousi = self.first[0]
                    self.reverse = self.first[2]
                    self.meisi = self.second[0]

                if self.keiyousi in self.dic['word'].values:
                    self.score = self.score + self.dic[self.dic['word'] == self.keiyousi]['score'].values[0]*self.reverse
                    self.scores[self.meisi] = self.score
                else:
                    print(self.keiyousi+":辞書に登録されていません")

            self.score = 0

        return self.scores
