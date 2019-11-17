import CaboCha
import pydot
import re
from IPython.display import Image, display_png

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #DEBUG を INFOに変えるとlogging.debugが出力されなくなる

class Morph:
    def __init__(self,id,surface,base,pos,pos1,pos2,pos3,feats,ne):
        self.id = id
        self.surface=surface
        self.base=base
        self.pos=pos
        self.pos1=pos1
        self.pos2=pos2
        self.pos3=pos3
        self.feats=[]
        self.ne = 12345
    
    def print_morph(self):
        print("##{} : {} {} {} {} {} {}##".format(self.id, self.surface,self.base,self.pos,self.pos1,self.pos2,self.pos3))
        
        
class Chunk:
    def __init__(self, id):
        self.id = id
        self.morphs=[]
        self.dst=-1
        self.srcs=[]
        self.head_pos = -1
        self.func_pos = -1
        self.score = -1

    def add_morph(self,morph):
        self.morphs.append(morph)

    def add_dst(self,dst):
        self.dst=dst

    def add_src(self,src):
        self.srcs.append(src)
        
    def add_chunk_info(self, hpos, fpos, score):
        self.head_pos = hpos
        self.func_pos = fpos
        self.score = score

    def print_chunk(self):
        print("Chunk {} : \n\tmorphs : ".format(self.id))
        for morph in self.morphs:
            print("\t\t",end="")
            morph.print_morph()
        print("\tdst : {}".format(self.dst))
        print("\tsrcs : { ",end="")
        for src in self.srcs:
            print(str(src)+" ",end="")
        print("}")

    def surfaces(self):
        surfaces=""
        for morph in self.morphs:
            if morph.pos!="記号":
                surfaces+=morph.surface
        return surfaces


   
def cabocha_make_novellist(text, cparser):
    text = re.split('[\n\t。 ]', text) #改行または句点で区切り配列化
    while '' in text:         #空行は削除
        text.remove('')
    
    novel_list=[] #
    for index,sentence in enumerate(text): 
        logging.debug(sentence)
        result = cparser.parse(sentence)
        
        sentence_list = [] ##
        chunk = Chunk(-1)
        
        for i in range(result.size()):
            token = result.token(i)
            
            if token.chunk != None:
                if chunk.id!=-1:
                    sentence_list.append(chunk)
                chunk = Chunk(len(sentence_list))
                chunk.add_dst(token.chunk.link)
                chunk.add_chunk_info(token.chunk.head_pos, token.chunk.func_pos, token.chunk.score)
            
            feats = token.feature.split(",")
            morph = Morph(len(chunk.morphs), token.surface, feats[6], feats[0], feats[1], feats[2], feats[3], feats, token.ne)
            chunk.add_morph(morph)

        if chunk.id!=-1:
            sentence_list.append(chunk)
    
        if len(sentence_list)>0:
            novel_list.append(sentence_list)
    return novel_list


def cabocha_dependency_visualize(novel_list, withstr=False):
    for sentence_list in novel_list:
        graph = []
        for chunk in sentence_list:
            src_str=chunk.surfaces()
            dst_str=""
            if chunk.dst!=-1:
                dst_str=sentence_list[chunk.dst].surfaces()
            if src_str!="" and dst_str!="":
                graph.append((src_str,dst_str))
                if withstr:
                    print("{}  =>  {}".format(src_str,dst_str))
        
        g=pydot.graph_from_edges(graph,directed=True)
        #g.write_png("result.png")
        display_png(Image(g.create_png()))


if __name__ == '__main__':
    parser = CaboCha.Parser()
    sentence = """
        私は人間です。

        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。
    """
    print(parser.parseToString(sentence))

    tree =  parser.parse(sentence)
    print(tree.toString(CaboCha.FORMAT_TREE))
    print(tree.toString(CaboCha.FORMAT_LATTICE))

    chunkId = 0
    for i in range(tree.size()):
        token = tree.token(i)
        if token.chunk != None:
            print(chunkId, token.chunk.link, token.chunk.head_pos, token.chunk.func_pos, token.chunk.score)
            chunkId += 1
        print(token.surface, token.feature, token.ne)

    parser = CaboCha.Parser()
    text = """
        私は人間です。
        呼吸と食事ができます。
        私は望遠鏡で泳ぐ少女を見た。
    """
    novel_list = cabocha_make_novellist(text, parser)

    novel_list[0][0].print_chunk()
    novel_list[0][1].print_chunk()
    novel_list[1][0].print_chunk()
    novel_list[1][1].print_chunk()
    novel_list[1][2].print_chunk()

    cabocha_dependency_visualize(novel_list, withstr=True)