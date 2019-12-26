from pyknp import Juman, KNP
import pydot
import re
from IPython.display import Image, display_png

import pandas as pd

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

##### get elements from "素性"
def fst_parsing_skel(fstring, pattern, none):
    repatter = re.compile(pattern)
    res = repatter.findall(fstring)
    if len(res)>0:
        result = res[0]
    else:
        result = none
    pfst = re.sub(pattern, "", fstring)
    return result, pfst

def fst_parsing_NormReprNotation(fstring):
    pattern = r"<正規化代表表記:(.+?)>"
    nrn, fstring = fst_parsing_skel(fstring, pattern, "")
    return nrn, fstring

def fst_parsing_YogenReprNotation(fstring):
    pattern = r"<用言代表表記:(.+?)>"
    yrn, fstring = fst_parsing_skel(fstring, pattern, "")
    return yrn, fstring

def fst_parsing_MainReprNotation(fstring):
    pattern = r"<主辞.?代表表記:(.+?)>"
    mrn, fstring = fst_parsing_skel(fstring, pattern, "")
    return mrn, fstring

def fst_parsing_particleCase(fstring):
    pattern = r"<係:(.+?)>"
    pc, fstring = fst_parsing_skel(fstring, pattern, "")
    return pc, fstring

def fst_parsing_taigen_yogen(fstring):
    tpat = r"<体言>"
    taigen, fstring = fst_parsing_skel(fstring, tpat, "")
    taigen = 1 if taigen=="<体言>" else 0

    ypat = r"<用言:(.)>"
    yogen, fstring = fst_parsing_skel(fstring, ypat, "")
    return taigen, yogen, fstring

def fst_parsing_adverb(fstring):
    pattern = r"<副詞>"
    adverb, fstring = fst_parsing_skel(fstring, pattern, "")
    adverb = 1 if adverb=="<副詞>" else 0
    return adverb, fstring

def fst_parsing_eid(fstring):
    pattern = r"<EID:([0-9]+?)>"
    eid, fstring = fst_parsing_skel(fstring, pattern, "-1")
    return int(eid), fstring

def fst_parsing_caseAnalysisResult(fstring):
    pattern = r"<格解析結果:(.+?)>"
    car, fstring = fst_parsing_skel(fstring, pattern, "")
    return car, fstring

def fst_parsing_head_tail(fstring):
    hpat = r"<文頭>"
    head, fstring = fst_parsing_skel(fstring, hpat, "")
    head = 1 if head=="<文頭>" else 0

    #tpat = r"<文末>"
    tpat = r"<ID:（文末）>"
    tail, fstring = fst_parsing_skel(fstring, tpat, "")
    #tail = 1 if tail=="<文末>" else 0
    tail = 1 if tail=="<ID:（文末）>" else 0
    return head, tail, fstring

def fst_parsing_EstimatedCase(fstring):
    pattern = r"<解析格:(.+?)>"
    ecase, fstring = fst_parsing_skel(fstring, pattern, "")
    return ecase, fstring

def fst_parsing_rentai_renyo(fstring):
    tpat = r"<連体修飾>"
    rentai, fstring = fst_parsing_skel(fstring, tpat, "")
    rentai = 1 if rentai=="<連体修飾>" else 0
    ypat = r"<連用要素>"
    renyo, fstring = fst_parsing_skel(fstring, ypat, "")
    renyo = 1 if renyo=="<連用要素>" else 0
    return rentai, renyo, fstring

def fst_parsing_denial(fstring):
    pattern = r"<否定表現>"
    deny, fstring = fst_parsing_skel(fstring, pattern, "")
    deny = 1 if deny=="<否定表現>" else 0
    return deny, fstring

def fst_parsing_predicates(fstring):
    pattern1 = r"<状態述語>"
    pred1, fstring = fst_parsing_skel(fstring, pattern1, "")
    pred1 = 1 if pred1=="<状態述語>" else 0

    pattern2 = r"<動態述語>"
    pred2, fstring = fst_parsing_skel(fstring, pattern2, "")
    pred2 = 1 if pred2=="<動態述語>" else 0

    return pred1, pred2, fstring

def get_nrn(chunk):
    #chunk.nrn.split("/")[0]
    nl = "".join([basis.split("/")[0] for basis in chunk.nrn.split("+")])
    return nl

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
Tag_series_columns = ['文番号', '文節番号', '基本句番号', 'ID', '表層','正規化代表表記','用言代表表記', '掛先ID', '係り受けタイプ','EID','係:','解析格','体言','用言','副詞','格解析結果', '素性']

class Tag:
    def __init__(self, sid, cid, tid, tag):
        self.sid = sid
        self.cid = cid
        self.tid = tid
        self.id = tag.tag_id
        self.midasi = "".join(mrph.midasi for mrph in tag.mrph_list())
        self.dst = tag.parent_id
        self.dpndtype = tag.dpndtype
        eid, fstring = fst_parsing_eid(tag.fstring)
        taigen, yogen, fstring = fst_parsing_taigen_yogen(fstring)
        adverb, fstring = fst_parsing_adverb(fstring)
        pc, fstring = fst_parsing_particleCase(fstring)
        car, fstring = fst_parsing_caseAnalysisResult(fstring)
        nrn, fstring = fst_parsing_NormReprNotation(fstring)
        yrn, fstring = fst_parsing_YogenReprNotation(fstring)
        ecase, fstring = fst_parsing_EstimatedCase(fstring)
        self.eid = eid          # EID
        self.pc = pc            # <係:>
        self.taigen = taigen    # 体言
        self.yogen = yogen      # 用言
        self.adverb = adverb    # 副詞
        self.car = car          # 格解析結果
        self.nrn = nrn          # 正規化代表表記
        self.yrn = yrn          # 用言代表表記
        self.ecase = ecase      # <解析格:>
        self.fstring = fstring  # その他の素性

    def make_tag_series_list(self):
        return [
            self.sid,
            self.cid,
            self.tid,
            self.id,
            self.midasi,
            self.nrn,
            self.yrn,
            self.dst,
            self.dpndtype,
            self.eid,
            self.pc,
            self.ecase,
            self.taigen,
            self.yogen,
            self.adverb,
            self.car,
            self.fstring
        ]


##### Chunk
Chunk_series_columns = ['文番号','文節番号','ID','src','見出し','掛先ID', '係り受けタイプ','正規化代表表記','主辞代表表記','係:','連体修飾','連用要素', '体言','用言','副詞','否定','状態述語','動態述語','素性']

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
        head, tail, fstring = fst_parsing_head_tail(fstring)
        rentai, renyo, fstring = fst_parsing_rentai_renyo(fstring)
        deny, fstring = fst_parsing_denial(fstring)
        pred1, pred2, fstring = fst_parsing_predicates(fstring)
        self.nrn = nrn
        self.mrn = mrn
        self.pc = pc
        self.rentai = rentai   # <連体修飾>
        self.renyo = renyo     # <連用要素>
        self.taigen = taigen
        self.yogen = yogen
        self.adverb = adverb
        self.isHead = head
        self.isTail = tail
        self.deny = deny       # <否定表現>
        self.pred1 = pred1     # <状態述語>
        self.pred2 = pred2     # <動態述語>
        self.fstring = fstring

    def make_chunk_series_list(self):
        return [
            self.sid,             # 文番号
            self.cid,             # 文節番号
            self.id,
            self.srcs,
            self.midasi,          # 見出し
            self.dst,             # 係り受け先文節番号
            self.dpndtype,        # 係り受けタイプ
            self.nrn,             # 正規化代表表記
            self.mrn,             # 主辞代表表記
            self.pc,              # 助詞の格
            self.rentai,          # <連体修飾>
            self.renyo,           # <連用要素>
            self.taigen,          # 体言
            self.yogen,           # 用言
            self.adverb,          # 副詞
            self.deny,            # 否定表現
            self.pred1,           # <状態述語>
            self.pred2,           # <動態述語>
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


def pyknp_morph2df(comment_list, output=False):
    df = pd.DataFrame(index=[], columns = Morph_series_columns)
    if output:
        print("/".join(Morph_series_columns))
    for sindex,sentence_list in enumerate(comment_list): 
        for cid, chunk in enumerate(sentence_list):
            for mid, mrph in enumerate(chunk.morphs):
                if output:
                    #print("[%d %d %s]%s###%s###"%(cid,mid,mrph.midasi, mrph.imis, mrph.repname))
                    print(mrph.make_morph_series_list())
                    #print(mrph.make_morph_series_list()[-2])
                # make series
                series = pd.Series(mrph.make_morph_series_list(), index=df.columns)
                df = df.append(series, ignore_index = True)
    return df


def pyknp_chunk2df(comment_list, output=False):
    df = pd.DataFrame(index=[], columns = Chunk_series_columns)
    if output:
        print("/".join(Chunk_series_columns))
    for sindex, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if output:
                print(chunk.make_chunk_series_list())
                #print(chunk.make_chunk_series_list()[-1])
            # make series
            series = pd.Series(chunk.make_chunk_series_list(), index = df.columns)
            df = df.append(series, ignore_index = True)
    return df

def pyknp_tag2df(comment_list, output=False):
    df = pd.DataFrame(index=[], columns = Tag_series_columns)
    if output:
        print("/".join(Tag_series_columns))
    for sindex,sentence_list in enumerate(comment_list): 
        for cid, chunk in enumerate(sentence_list):
            for tid, tag in enumerate(chunk.tags):
                if output:
                    #print("[%d %d %s]###%s###"%(cid,tid,tag.midasi, tag.fstring))
                    print(tag.make_tag_series_list())
                    #print(tag.car)
                    #print(tag.fstring)
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

def search_adverb(comment_list, sid, cid):
    adverbs = []
    for id in comment_list[sid][cid].srcs:
        if comment_list[sid][id].adverb==1:
            adverbs.append(comment_list[sid][id])
    return adverbs



def pyknp_search_AdjectiveNoun(comment_list): #形容詞連体修飾-名詞(美味しいご飯)
    def chunk_isRoot(chunk):
        if chunk.yogen=="形" and chunk.pc=="連格":
            return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if chunk.taigen==1:
            return True
        else:
            return False
    
    def chunk_stop(chunk):
        if chunk.dst==-1 or chunk.isTail:
            return True
        else:
            return False

    pair_chunks = []
    for sid, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if chunk_isRoot(chunk):
                id = chunk.cid
                if chunk_stop(chunk):
                    continue
                dst_chunk = sentence_list[chunk.dst]
                if chunk_isChild(dst_chunk):
                    adverbs = search_adverb(comment_list, chunk.sid, chunk.cid) # 形容詞にかかる副詞を探索
                    pair_chunks.append([[chunk, adverbs], dst_chunk])
    
    search_result = [[
        get_nrn(i[0][0]),                         # adj
        "/".join([get_nrn(c) for c in i[0][1]]),  # adv
        i[0][0].deny,                             # not
        get_nrn(i[1]),                            # noun
        "",                                       # nokaku (now null)
        i[1].deny                                 # not
    ]for i in pair_chunks]

    return search_result


def pyknp_search_NounAdjective(comment_list): #名詞-形容詞連用(ご飯は美味しい)
    def chunk_isRoot(chunk):
        if chunk.yogen=="形" and chunk.rentai==0:
            return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if chunk.taigen==1:
            for tag in chunk.tags:
                if tag.ecase=="ガ":
                    return True
        return False

    def chunk_stop(chunk):
        #if chunk.dst==-1 or chunk.isTail:
        if chunk.pred1==1 or chunk.pred2==1:
            return True
        else:
            return False

    pair_chunks = []
    for sid, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if chunk_isRoot(chunk):
                stack = []
                stack.extend(chunk.srcs)
                while len(stack)>0:
                    next_id = stack.pop()
                    next_chunk = sentence_list[next_id]
                    if chunk_stop(next_chunk):
                        continue
                    if chunk_isChild(next_chunk):
                        adverbs = search_adverb(comment_list, chunk.sid, chunk.cid)
                        tokakus = []
                        now = next_chunk
                        while(len(now.srcs)>0):
                            flag = 0
                            for sr in now.srcs:
                                if comment_list[sid][sr].taigen==1 and comment_list[sid][sr].pc=="ト格":
                                    now = comment_list[sid][sr]
                                    tokakus.append(now)
                                    flag=1
                                    break
                            if flag==0:
                                break
                        tokakus.insert(0, next_chunk)
                        nokakus_list = []
                        for tokaku in tokakus:
                            nokakus = []
                            for id in tokaku.srcs:
                                if comment_list[sid][id].pc=="ノ格":
                                    nokakus.append(comment_list[sid][id])
                            nokakus_list.append(nokakus)
                        assert len(tokakus) == len(nokakus_list)
                        pair_chunks.append([[tokakus, nokakus_list], [chunk, adverbs]])
                    stack.extend(next_chunk.srcs)

    search_result = []
    for cl in pair_chunks:
        for i in range(len(cl[0][0])):
            search_result.append([
                get_nrn(cl[1][0]),                                       # adj
                "/".join([get_nrn(c) for c in cl[1][1]]),                # adv
                cl[1][0].deny,                                           # not
                get_nrn(cl[0][0][i]),                                    # noun
                "/".join([get_nrn(c) for c in cl[0][1][i]]),             # nokaku
                cl[0][0][i].deny                                         # not
            ])

    return search_result


def pyknp_search_VerbNoun(comment_list): #動詞-名詞(飽きない味)
    def chunk_isRoot(chunk):
        if chunk.yogen=="動" and chunk.rentai==1:
            return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if chunk.taigen==1:
            return True
        else:
            return False
        
    def chunk_stop(chunk):
        if chunk.dst==-1 or chunk.isTail:
            return True
        else:
            return False
    
    pair_chunks = []
    for sid, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if chunk_isRoot(chunk):
                id = chunk.cid
                if chunk_stop(chunk):
                    continue
                dst_chunk = sentence_list[chunk.dst]
                if chunk_isChild(dst_chunk):
                    adverbs = search_adverb(comment_list, chunk.sid, chunk.cid)
                    pair_chunks.append([[chunk, adverbs], dst_chunk])
    
    search_result = [[
        get_nrn(i[0][0]),                        # verb
        "/".join([get_nrn(c) for c in i[0][1]]), # adv
        i[0][0].deny,                            # not
        get_nrn(i[1]),                           # noun
        "",                                      # nokaku(now null)
        i[1].deny                                # not
    ]for i in pair_chunks]

    return search_result


def pyknp_search_NounVerb(comment_list): #名詞-動詞(私は飽きた)
    def chunk_isRoot(chunk):
        if chunk.yogen=="動" and chunk.rentai==0:
            return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if chunk.taigen==1:
            for tag in chunk.tags:
                if tag.ecase=="ガ":
                    return True
        return False
    
    def chunk_stop(chunk):
        #if chunk.dst==-1 or chunk.isTail:
        if chunk.pred1==1 or chunk.pred2==1:
            return True
        else:
            return False

    pair_chunks = []
    for sid, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if chunk_isRoot(chunk):
                stack = []
                stack.extend(chunk.srcs)
                while len(stack)>0:
                    next_id = stack.pop()
                    next_chunk = sentence_list[next_id]
                    if chunk_stop(next_chunk):
                        continue
                    if chunk_isChild(next_chunk):
                        adverbs = search_adverb(comment_list, chunk.sid, chunk.cid)
                        tokakus = []
                        now = next_chunk
                        while(len(now.srcs)>0):
                            flag = 0
                            for sr in now.srcs:
                                if comment_list[sid][sr].taigen==1 and comment_list[sid][sr].pc=="ト格":
                                    now = comment_list[sid][sr]
                                    tokakus.append(now)
                                    flag = 1
                                    break
                            if flag==0:
                                break
                        tokakus.insert(0, next_chunk)
                        nokakus_list = []
                        for tokaku in tokakus:
                            nokakus = []
                            for id in tokaku.srcs:
                                if comment_list[sid][id].pc=="ノ格":
                                    nokakus.append(comment_list[sid][id])
                            nokakus_list.append(nokakus)
                        assert len(tokakus) == len(nokakus_list)
                        pair_chunks.append([[tokakus, nokakus_list], [chunk, adverbs]])
                    stack.extend(next_chunk.srcs)

    search_result = []
    for cl in pair_chunks:
        for i in range(len(cl[0][0])):
            search_result.append([
                get_nrn(cl[1][0]),                                       # adj
                "/".join([get_nrn(c) for c in cl[1][1]]),                # adv
                cl[1][0].deny,                                           # not
                get_nrn(cl[0][0][i]),                                    # noun
                "/".join([get_nrn(c) for c in cl[0][1][i]]),             # nokaku
                cl[0][0][i].deny                                         # not
            ])

    return search_result


def pyknp_search_NounNoun(comment_list):
    def chunk_isRoot(chunk):
        if chunk.taigen==1:
            for tag in chunk.tags:
                if tag.ecase=="ガ":
                    return True
        else:
            return False
    
    def chunk_isChild(chunk):
        if chunk.taigen==1:
            return True
        return False
    
    def chunk_stop(chunk):
        if chunk.dst==-1 or chunk.isTail:
            return True
        else:
            return False

    pair_chunks = []
    for sid, sentence_list in enumerate(comment_list):
        for cid, chunk in enumerate(sentence_list):
            if chunk_isRoot(chunk):
                id = chunk.cid
                if chunk_stop(chunk):
                    continue
                dst_chunk = sentence_list[chunk.dst]
                if chunk_isChild(dst_chunk):
                    pair_chunks.append([chunk, dst_chunk])

    search_result = [[
        get_nrn(i[1]),      # noun
        "",                 # nokaku (now null)
        i[1].deny,          # not
        get_nrn(i[0]),      # noun
        "",                 # nokaku (now null)
        i[0].deny           # not
    ]for i in pair_chunks]
    return search_result


def knp_analyze(text, knp, lines_split=False, visualize=False):
    comment_list = pyknp_make_commentlist(text, knp, lines_split=False)
    if visualize:
        pyknp_dependency_visualize(comment_list, withstr=True)

    adj_noun = pyknp_search_AdjectiveNoun(comment_list)
    noun_adj = pyknp_search_NounAdjective(comment_list)
    verb_noun = pyknp_search_VerbNoun(comment_list)
    noun_verb = pyknp_search_NounVerb(comment_list)
    noun_noun = pyknp_search_NounNoun(comment_list)

    print("adj_noun\n", adj_noun)
    print("noun_adj\n", noun_adj)
    print("verb_noun\n", verb_noun)
    print("noun_verb\n", noun_verb)
    print("noun_noun\n", noun_noun)

    result = adj_noun + noun_adj + verb_noun + noun_verb + noun_noun
    return result


if __name__ == '__main__':
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。"""
    #text = "私は人間です。"

    comment_list = pyknp_make_commentlist(text, knp)
    pyknp_dependency_visualize(comment_list, withstr=True)

    pyknp_morph2df(comment_list, output=True)

    pyknp_tag2df(comment_list, output=True)

    pyknp_chunk2df(comment_list, output=True)