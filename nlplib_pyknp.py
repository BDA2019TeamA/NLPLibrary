from pyknp import Juman, KNP
import pydot
import re
from IPython.display import Image, display_png

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #DEBUG を INFOに変えるとlogging.debugが出力されなくなる

def pyknp_make_novellist(text, kparser):
    text = re.split('[\n\t。 ]', text) #改行または句点で区切り配列化
    while '' in text:         #空行は削除
        text.remove('')
    
    result_list=[] #
    for index,sentence in enumerate(text): 
        logging.debug(sentence)
        result = kparser.parse(sentence)
        result_list.append(result)
    
    return result_list


def pyknp_dependency_visualize(result_list, withstr=False):
    for result in result_list:
        graph = []
        bnst_dic = dict((x.bnst_id, x) for x in result.bnst_list())
        for bnst in result.bnst_list():
            if bnst.parent_id != -1:
                src_str = "".join(mrph.midasi for mrph in bnst.mrph_list())
                dst_str = "".join(mrph.midasi for mrph in bnst_dic[bnst.parent_id].mrph_list())
                graph.append((src_str, dst_str))
                if withstr:
                    print("{}  =>  {}".format(src_str,dst_str))

        g=pydot.graph_from_edges(graph,directed=True)
        #g.write_png("result.png")
        display_png(Image(g.create_png()))



if __name__ == '__main__':
    juman = Juman()
    res = juman.analysis("すもももももももものうち")
    for m in res.mrph_list():
        print (m.midasi, m.yomi, m.genkei, m.hinsi, m.bunrui, m.katuyou1, m.katuyou2, m.imis, m.repname)

    #knp = KNP(option = "-tab -anaphora)
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    #result = knp.parse("すもももももももものうち")
    result = knp.parse("太郎は太っている。彼はいつも何か食べている。")

    for bnst in result.bnst_list():
        print(bnst.midasi)
    
    print("\n文節")
    for bnst in result.bnst_list(): # 各文節へのアクセス
        print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%d, 素性:%s" \
                % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring))

    print("\n基本句")
    for tag in result.tag_list(): # 各基本句へのアクセス
        print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親基本句ID:%d, 素性:%s" \
                % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring))

    print("\n形態素")
    for mrph in result.mrph_list(): # 各形態素へのアクセス
        print("\tID:%d, 見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                % (mrph.mrph_id, mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))

    knp = KNP(jumanpp=True)
    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。"""
    #text = "私は人間です。"

    novel_list = pyknp_make_novellist(text, knp)
    pyknp_dependency_visualize(novel_list, withstr=True)