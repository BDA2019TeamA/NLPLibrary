from pyknp import Juman, KNP
import pydot
import re
from IPython.display import Image, display_png

import pandas as pd

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

##### Morph

def imis_parsing_repname(string):
    sl = string.split(" ")
    place = -1
    for i, info in enumerate(sl):
        if info[:5]=="代表表記:":
            place = i
    sl.pop(place)
    return " ".join(sl)

Morph_series_columns = ['文番号','文節番号', '形態素番号', 'ID','表層','読み','原形','品詞','品詞細分類','活用1','活用2', '意味情報', '代表表記', '代表表記(ひらがな))']

class Morph:
    def __init__(self, sid, cid, mid, mrph):
        self.sid = sid # sentence_id
        self.cid = cid # chunk_id
        self.mid = mid # morph_id
        self.id = mrph.mrph_id
        self.midasi = mrph.midasi
        self.yomi = mrph.yomi
        self.genkei = mrph.genkei
        self.hinsi = mrph.hinsi
        self.bunrui = mrph.bunrui
        self.katsuyou1 = mrph.katuyou1
        self.katsuyou2 = mrph.katuyou2
        self.imis = imis_parsing_repname(mrph.imis)
        if mrph.repname=="":
            self.repname = ""
            self.repname_kana = ""
        else:
            self.repname = mrph.repname.split("/")[0]
            self.repname_kana = mrph.repname.split("/")[1]

    def make_morph_series_list(self):
        return [
            self.sid,            #文番号
            self.cid,            #文節番号
            self.mid,            #形態素番号
            self.id,
            self.midasi,         #表層
            self.yomi,           #読み
            self.genkei,         #原形     
            self.hinsi,          #品詞
            self.bunrui,         #品詞細分類
            self.katsuyou1,      #活用1
            self.katsuyou2,      #活用2
            self.imis,           #意味情報
            self.repname,        #代表表記
            self.repname_kana    #代表表記(ひらがな)
        ]

##### Tag

Tag_series_columns = ['文番号', '文節番号', '基本句番号', 'ID', '表層', '掛先ID', '係り受けタイプ', '素性']

class Tag:
    def __init__(self, sid, cid, tid, tag):
        self.sid = sid
        self.cid = cid
        self.tid = tid
        self.id = tag.tag_id
        self.midasi = "".join(mrph.midasi for mrph in tag.mrph_list())
        self.dst = tag.parent_id
        self.dpndtype = tag.dpndtype
        self.fstring = tag.fstring

    def make_tag_series_list(self):
        return [
            self.sid,
            self.cid,
            self.tid,
            self.id,
            self.midasi,
            self.dst,
            self.dpndtype,
            self.fstring
        ]

##### Chunk

def fst_parsing_NormReprNotation(fstring):
    pattern = r"<正規化代表表記:(.+?)>"
    repatter = re.compile(pattern)
    res = repatter.findall(fstring)
    if len(res)>0:
        nrn = res[0]
    else:
        nrn = 0
    pfst = re.sub(pattern, "", fstring)
    return nrn, pfst

def fst_parsing_MainReprNotation(fstring):
    pattern = r"<主辞.?代表表記:(.+?)>"
    repatter = re.compile(pattern)
    res = repatter.findall(fstring)
    if len(res)>0:
        mrn = res[0]
    else:
        mrn = 0
    pfst = re.sub(pattern, "", fstring)
    return mrn, pfst

def fst_parsing_particleCase(fstring):
    pattern = r"<係:(.+?)>"
    repatter = re.compile(pattern)
    res = repatter.findall(fstring)
    if len(res)>0:
        pc = res[0]
    else:
        pc = 0
    pfst = re.sub(pattern, "", fstring)
    return pc, pfst

def fst_parsing_taigen_yogen(fstring):
    tpat = r"<体言>"
    trepat = re.compile(tpat)
    tres = trepat.findall(fstring)
    if len(tres)>0:
        taigen = 1
    else:
        taigen = 0
    fstring = re.sub(trepat, "", fstring)

    ypat = r"<用言:(.)>"
    yrepat = re.compile(ypat)
    yres = yrepat.findall(fstring)
    if len(yres)>0:
        yogen = yres[0]
    else:
        yogen = ""
    fstring = re.sub(yrepat, "", fstring)
    return taigen, yogen, fstring

def fst_parsing_adverb(fstring):
    pattern = r"<副詞>"
    repatter = re.compile(pattern)
    res = repatter.findall(fstring)
    if len(res)>0:
        adverb = 1
    else:
        adverb = 0
    fstring = re.sub(pattern, "", fstring)
    return adverb, fstring

Chunk_series_columns = ['文番号','文節番号','ID','見出し','掛先ID', '係り受けタイプ','正規化代表表記','主辞代表表記','助詞の格', '体言','用言','副詞','素性']

class Chunk:
    def __init__(self, sid, cid, bnst):
        self.morphs = []
        self.tags = []
        self.sid = sid
        self.cid = cid
        self.id = bnst.bnst_id
        self.dst = bnst.parent_id
        self.srcs = []
        self.midasi = "".join(mrph.midasi for mrph in bnst.mrph_list())
        self.dpndtype = bnst.dpndtype
        nrn, fstring = fst_parsing_NormReprNotation(bnst.fstring)
        mrn, fstring = fst_parsing_MainReprNotation(fstring)
        pc, fstring = fst_parsing_particleCase(fstring)
        taigen, yogen, fstring = fst_parsing_taigen_yogen(fstring)
        adverb, fstring = fst_parsing_adverb(fstring)
        self.nrn = nrn
        self.mrn = mrn
        self.pc = pc
        self.taigen = taigen
        self.yogen = yogen
        self.adverb = adverb
        self.fstring = fstring

    def make_chunk_series_list(self):
        return [
            self.sid,             # 文番号
            self.cid,             # 文節番号
            self.id,
            self.midasi,          # 見出し
            self.dst,             # 係り受け先文節番号
            self.dpndtype,        # 係り受けタイプ
            self.nrn,             # 正規化代表表記
            self.mrn,             # 主辞代表表記
            self.pc,              # 助詞の格
            self.taigen,          # 体言
            self.yogen,           # 用言
            self.adverb,          # 副詞
            self.fstring          # 残りの素性
        ]
    



def pyknp_make_commentlist(text, kparser, lines_split=True):
    if lines_split:
        text = re.split('[\n\t。 ]', text) #改行または句点で区切り配列化
        while '' in text:         #空行は削除
            text.remove('')
    else:
        text = [text]
    
    comment_list=[] #
    for sentence_id, sentence in enumerate(text):
        sentence_list = [] ##
        logging.debug(sentence)
        result = kparser.parse(sentence)

        for chunk_id,bnst in enumerate(result.bnst_list()):
            sentence_list.append(Chunk(sentence_id, chunk_id, bnst))
        
        for chunk_id,chunk in enumerate(sentence_list):
            if chunk.dst != -1:
                sentence_list[chunk.dst].srcs.append(chunk_id)
        
        for chunk_id, bnst in enumerate(result.bnst_list()):
            for tag_id, tag in enumerate(bnst.tag_list()):
                sentence_list[chunk_id].tags.append(Tag(sentence_id, chunk_id, tag_id, tag))
        
        for chunk_id, bnst in enumerate(result.bnst_list()):
            for morph_id, mrph in enumerate(bnst.mrph_list()):
                sentence_list[chunk_id].morphs.append(Morph(sentence_id, chunk_id, morph_id, mrph))

        comment_list.append(sentence_list)
    return comment_list


def pyknp_morph2df(comment_list):
    df = pd.DataFrame(index=[], columns = Morph_series_columns)
    for sindex,sentence_list in enumerate(comment_list): 
        for cid, chunk in enumerate(sentence_list):
            for mid, mrph in enumerate(chunk.morphs):
                #print("[%d %d %s]%s###%s###"%(cid,mid,mrph.midasi, mrph.imis, mrph.repname))
                # make series
                series = pd.Series(mrph.make_morph_series_list(), index=df.columns)
                df = df.append(series, ignore_index = True)
    return df


def pyknp_chunk2df(comment_list):
    df = pd.DataFrame(index=[], columns = Chunk_series_columns)
    for sindex, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            #print(sindex, cid, chunk.midasi, fstring)
            # make series
            series = pd.Series(chunk.make_chunk_series_list(), index = df.columns)
            df = df.append(series, ignore_index = True)
    return df

def pyknp_tag2df(comment_list):
    df = pd.DataFrame(index=[], columns = Tag_series_columns)
    for sindex,sentence_list in enumerate(comment_list): 
        for cid, chunk in enumerate(sentence_list):
            for tid, tag in enumerate(chunk.tags):
                #print("[%d %d %s]###%s###"%(cid,tid,tag.midasi, tag.fstring))
                # make series
                series = pd.Series(tag.make_tag_series_list(), index=df.columns)
                df = df.append(series, ignore_index = True)
    return df


def pyknp_dependency_visualize(comment_list, withstr=False):
    for sentence_list in comment_list:
        graph = []
        for cid,chunk in enumerate(sentence_list):
            if chunk.dst != -1:
                src_str = str(cid)+":"+chunk.midasi
                dst_str = str(chunk.dst)+":"+sentence_list[chunk.dst].midasi
                graph.append((src_str, dst_str))
                if withstr:
                    print("{}  =>  {}".format(src_str,dst_str))

        g=pydot.graph_from_edges(graph,directed=True)
        #g.write_png("result.png")
        display_png(Image(g.create_png()))


def pyknp_search_1(comment_list):
    def chunk_isNextSentence(chunk):
        if chunk.midasi[-1]=="。":
            return True
        else:
            return False
    
    def chunk_isParent(chunk):
        if chunk.yogen=="形":
            return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if 1==1:
            return True
        else:
            return False

    for sid, sentence_list in enumerate(comment_list):
        next_sentence = -1
        stack = []


if __name__ == '__main__':
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。"""
    #text = "私は人間です。"

    comment_list = pyknp_make_commentlist(text, knp)
    pyknp_dependency_visualize(comment_list, withstr=True)