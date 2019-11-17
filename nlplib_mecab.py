import pandas as pd
import re
from natto import MeCab

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def mecab_parse2df(text, mparser):
    df = pd.DataFrame(index=[], columns=['文番号','表層', '品詞1','品詞2','品詞3','品詞4','原型','cost','posID'])
    
    text = re.split('[\n\t。 ]', text) #改行または句点で区切り配列化
    while '' in text:         #空行は削除
        text.remove('')

    for index,sentence in enumerate(text): 
        logging.debug(sentence)
        nodes = mparser.parse(sentence,as_nodes=True)
        for node in nodes:
            if not node.is_eos():
                feature = node.feature.split(',')
                series = pd.Series( [
                    index,          #文番号
                    node.surface,   #表層
                    feature[0],     #品詞1
                    feature[1],     #品詞2     
                    feature[2],     #品詞3
                    feature[3],     #品詞4
                    feature[6],     #原型
                    node.cost,      #コスト
                    node.posid      #品詞番号
                ], index=df.columns)
                df = df.append(series, ignore_index = True)
    return df



if __name__ == '__main__':
    parser = MeCab("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
    #parser = MeCab()
    nodes = parser.parse("私は人間です。",as_nodes=True)

    for node in nodes:
        if not node.is_eos():
            print(node.surface, " : ", node.feature, node.cost, node.posid)

    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。
    """
    df = mecab_parse2df(text, parser)
    print(df)