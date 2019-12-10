from pyknp import Juman, KNP
import pydot
import re
from IPython.display import Image, display_png

import pandas as pd

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Morph():
    def __init__(self, id, mrph):
        self.id = id
        self.knpid = mrph.mrph_id
        self.midasi = mrph.midasi
        self.yomi = mrph.yomi
        self.genkei = mrph.genkei
        self.hinsi = mrph.hinsi
        self.bunrui = mrph.bunrui
        self.katsuyou1 = mrph.katuyou1
        self.katsuyou2 = mrph.katuyou2
        self.imis = mrph.imis
        self.repname = mrph.repname

class Chunk():
    def __init__(self, id, bnst):
        self.morphs = []
        self.id = id
        self.knpid = bnst.bnst_id
        self.dst = bnst.parent_id
        self.srcs = []
        self.midasi = "".join(mrph.midasi for mrph in bnst.mrph_list())
        self.dpndtype = bnst.dpndtype
        self.fstring = bnst.fstring


def pyknp_make_commentlist(text, kparser):
    text = re.split('[\n\t。 ]', text) #改行または句点で区切り配列化
    while '' in text:         #空行は削除
        text.remove('')
    
    comment_list=[] #
    for index, sentence in enumerate(text):
        sentence_list = [] ##
        logging.debug(sentence)
        result = kparser.parse(sentence)

        for id,bnst in enumerate(result.bnst_list()):
            sentence_list.append(Chunk(id, bnst))
        
        for id,chunk in enumerate(sentence_list):
            if chunk.dst != -1:
                sentence_list[chunk.dst].srcs.append(id)
        
        for bid, bnst in enumerate(result.bnst_list()):
            for mid, mrph in enumerate(bnst.mrph_list()):
                sentence_list[bid].morphs.append(Morph(mid, mrph))

        comment_list.append(sentence_list)
    return comment_list


def pyknp_morph2df(comment_list):
    df = pd.DataFrame(index=[], columns=['文番号','文節番号', '形態素番号','表層','読み','原形','品詞','品詞細分類','活用1','活用2', '意味情報', '代表表記'])

    for sindex,sentence_list in enumerate(comment_list): 
        for cid, chunk in enumerate(sentence_list):
            for mid, mrph in enumerate(chunk.morphs):
                series = pd.Series( [
                    sindex,          #文番号
                    cid,             #文節番号
                    mid,             #形態素番号
                    mrph.midasi,        #表層
                    mrph.yomi,          #読み
                    mrph.genkei,        #原形     
                    mrph.hinsi,      #品詞
                    mrph.bunrui,     #品詞細分類
                    mrph.katsuyou1,  #活用1
                    mrph.katsuyou2,     #活用2
                    mrph.imis,          #意味情報
                    mrph.repname        #代表表記

                ], index=df.columns)
                df = df.append(series, ignore_index = True)
    return df


def pyknp_dependency_visualize(comment_list, withstr=False):
    for sentence_list in comment_list:
        graph = []
        for chunk in sentence_list:
            if chunk.dst != -1:
                src_str = chunk.midasi
                dst_str = sentence_list[chunk.dst].midasi
                graph.append((src_str, dst_str))
                if withstr:
                    print("{}  =>  {}".format(src_str,dst_str))

        g=pydot.graph_from_edges(graph,directed=True)
        #g.write_png("result.png")
        display_png(Image(g.create_png()))

if __name__ == '__main__':
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。"""
    #text = "私は人間です。"

    comment_list = pyknp_make_commentlist(text, knp)
    pyknp_dependency_visualize(comment_list, withstr=True)