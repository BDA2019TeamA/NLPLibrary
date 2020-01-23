import pickle
from nlplib_pyknp2 import *
import re
import traceback
import sys

def review_processing(review):
    review = re.sub(r"#", "　", review)
    review = re.sub(r"\ ", "　", review)
    review = re.sub(r"https?://(.+?)[,\ 　\"\n]", "", review)
    review = re.sub(r"\((.*?)\)", "", review)
    review = re.sub(r"（(.*?)）", "", review)
    review = re.sub(r"\t", "　", review)
    review = re.sub(r"0", "０", review)
    review = re.sub(r"1", "１", review)
    review = re.sub(r"2", "２", review)
    review = re.sub(r"3", "３", review)
    review = re.sub(r"4", "４", review)
    review = re.sub(r"5", "５", review)
    review = re.sub(r"6", "６", review)
    review = re.sub(r"7", "７", review)
    review = re.sub(r"8", "８", review)
    review = re.sub(r"9", "９", review)
    review = re.sub(r"/", "／", review)
    review = re.sub(r"~", "〜", review)
    if len(review)>1:
        if review[0]=='"':
            review = review[1:]
    elif len(review)==1 and review[0]=='"':
        review = ""
    if len(review)>1:
        if review[-1]=='"':
            review = review[:-1]
    elif len(review)==1 and review[0]=='"':
        review = ""
    return review


def makelist_retty(datafile):
    datas = []
    with open(datafile) as coms:
        allstr = coms.read().split("\n")
        for num, rev in enumerate(allstr):
            if rev!="":
                rev_list = rev.split(",")
                rid = rev_list[0]
                url = rev_list[1]
                review = ",".join(rev_list[2:-3])
                storeid = rev_list[-3]
                reviewid = rev_list[-2]
                score = rev_list[-1]
                datas.append([rid, url, review, storeid, reviewid, score])
    return datas

def makelist_tabelog(datafile):
    datas = []
    with open(datafile) as coms:
        allstr = coms.read().split("\n")
        for num, rev in enumerate(allstr):
            if rev!="":
                rev_list = rev.split(",")
                rid, CP, url = rev_list[:3]
                rid = rid[:-2]
                review = ",".join(rev_list[3:-7])
                service_score, storeid, reviewid, taste, evaluation, drink, env = rev_list[-7:]
                datas.append([rid, url, review, CP, service_score, storeid, reviewid, taste, evaluation, drink, env])
    return datas

def makelist_gurunabi(datafile):
    datas = []
    with open(datafile) as coms:
        allstr = coms.read().split("\n")
        for num, rev in enumerate(allstr):
            if rev!="":
                rev_list = rev.split(",")
                rid = rev_list[0]
                storeid = rev_list[1][1:-1]
                url = rev_list[2][1:-1]
                reviewid = rev_list[3][1:-1]
                nickname = rev_list[4][1:-1]
                review = ",".join(rev_list[5:])
                datas.append([rid, storeid, url, reviewid, nickname, review])
    return datas


def makedump_retty(knp, datas, begin, num, dirname, lines_split=False, debug=False):
    f = open("./"+dirname+"/log"+str(begin//100), "w")
    result = []
    end = min(begin+num, 64598)
    for i, data in enumerate(datas[begin:end]):
        print(i)
        review = review_processing(data[2])
        reviewid = data[0]

        comment_list = pyknp_make_commentlist(review, knp, lines_split=lines_split, logfile=f)
        data.append(comment_list)
        result.append(data)
        if debug:
            for j in knp_analyze_from_commentlist(comment_list):
                print(j, file=f)
    f.close()

    with open('./'+dirname+'/knpresult_'+str(begin//100)+'.pickle', 'wb') as f:
        pickle.dump(result, f)
    return result


def makedump_tabelog(knp, datas, begin, num, dirname, lines_split=False, debug=False):
    f = open("./"+dirname+"/log"+str(begin//100), "w")
    result = []
    end = min(begin+num, 73677)
    for i, data in enumerate(datas[begin:end]):
        print(i)
        review = review_processing(data[2])

        comment_list = pyknp_make_commentlist(review, knp, lines_split=lines_split, logfile=f)
        data.append(comment_list)
        result.append(data)
        if debug:
            for j in knp_analyze_from_commentlist(comment_list):
                print(j, file=f)
    f.close()

    with open('./'+dirname+'/knpresult_'+str(begin//100)+'.pickle', 'wb') as f:
        pickle.dump(result, f)
    return result

def makedump_gurunabi(knp, datas, begin, num, dirname, lines_split=False, debug=False):
    f = open("./"+dirname+"/log"+str(begin//100), "w")
    result = []
    end = min(begin+num, 1973)
    for i, data in enumerate(datas[begin:end]):
        print(i)
        review = review_processing(data[-1])

        comment_list = pyknp_make_commentlist(review, knp, lines_split=lines_split, logfile=f)
        data.append(comment_list)
        result.append(data)
        if debug:
            for j in knp_analyze_from_commentlist(comment_list):
                print(j, file=f)
    f.close()

    with open('./'+dirname+'/knpresult_'+str(begin//100)+'.pickle', 'wb') as f:
        pickle.dump(result, f)
    return result


def makedumps_retty(datas, begin, num, dirname, lines_split=False, debug=False):
    knp = KNP(option = '-tab -anaphora', jumanpp=True, timeout=30)
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_retty(knp, datas, 100*(begin_id + i), 100, dirname=dirname, lines_split=lines_split, debug=debug)

def makedumps_tabelog(datas, begin, num, dirname, lines_split=False, debug=False):
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_tabelog(knp, datas, 100*(begin_id + i), 100, dirname=dirname, lines_split=lines_split, debug=debug)

def makedumps_gurunabi(datas, begin, num, dirname, lines_split=False, debug=False):
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_gurunabi(knp, datas, 100*(begin_id + i), 100, dirname=dirname, lines_split=lines_split, debug=debug)


def checkdump(dirname, dump_id):
    with open('./'+dirname+'/knpresult_'+str(dump_id)+'.pickle', 'rb') as f:
        results = pickle.load(f)
        print(len(results))
        for result in results:
            try:
                knp_analyze_from_commentlist(result[-1], visualize=False)
            except Exception:
                print()
        print(len(results))


def get_fromdump(dirname, id):
    filenum = id//100
    ids = id % 100
    with open('./'+dirname+'/knpresult_'+str(filenum)+'.pickle', 'rb') as f:
        results = pickle.load(f)
        comment_list = results[ids][-1]
    return comment_list


def analyze_dump(dump_id_s, num, dirname, out_filename, separate_part=False, case=[0,0,0]):
    with open(out_filename,"w") as out:
        print("レビューid,動詞or形容詞or名詞,副詞,否定,対象名詞,ノ格,否定", file=out)
        for i in range(dump_id_s, dump_id_s+num):
            with open('./'+dirname+'/knpresult_'+str(i)+'.pickle', 'rb') as f:
                knp_results = pickle.load(f)
                mean = []
                for j, result in enumerate(knp_results):
                    try:
                        if separate_part:
                            analyze_result = []
                            if case[0]==1:
                                analyze_result += knp_analyze_from_commentlist_adj(result[-1], visualize=False)
                            if case[1]==1:
                                analyze_result += knp_analyze_from_commentlist_verb(result[-1], visualize=False)
                            if case[2]==1:
                                analyze_result += knp_analyze_from_commentlist_nounnoun(result[-1], visualize=False)
                        else:
                            analyze_result = knp_analyze_from_commentlist(result[-1], visualize=False)
                        for el in analyze_result:
                            el.insert(0, str(result[0]))
                            mean.append(el)
                    except Exception:
                        print(i,j, "###error###")
                        traceback.print_exc(file=sys.stdout)
                        sleep(1)
                for m in mean:
                    print(','.join(m), file=out)


def analyze_dump_fromlist(dump_list, dirname, out_filename, separate_part=False, case=[0,0,0]):
    with open(out_filename,"w") as out:
        print("レビューid,動詞or形容詞or名詞,副詞,否定,対象名詞,ノ格,否定", file=out)
        for i in dump_list:
            with open('./'+dirname+'/knpresult_'+str(i)+'.pickle', 'rb') as f:
                knp_results = pickle.load(f)
                mean = []
                for j, result in enumerate(knp_results):
                    try:
                        if separate_part:
                            analyze_result = []
                            if case[0]==1:
                                analyze_result += knp_analyze_from_commentlist_adj(result[-1], visualize=False)
                            if case[1]==1:
                                analyze_result += knp_analyze_from_commentlist_verb(result[-1], visualize=False)
                            if case[2]==1:
                                analyze_result += knp_analyze_from_commentlist_nounnoun(result[-1], visualize=False)
                        else:
                            analyze_result = knp_analyze_from_commentlist(result[-1], visualize=False)
                        for el in analyze_result:
                            el.insert(0, str(result[0]))
                            mean.append(el)
                    except Exception:
                        print(i,j, "###error###")
                        traceback.print_exc(file=sys.stdout)
                        sleep(1)
                for m in mean:
                    print(','.join(m), file=out)


def wakachi(begin, num, dirname, out_filename):
    assert begin%100==0 and num%100==0
    start = begin
    end = begin+num
    with open(out_filename,"w") as out:
        for i in range(start//100, end//100):
            with open('./'+dirname+'/knpresult_'+str(i)+'.pickle', 'rb') as f:
                knp_results = pickle.load(f)
                for j, result in enumerate(knp_results):
                    comment_list = result[-1]
                    for sid, sentence_list in enumerate(comment_list):
                        for cid, chunk in enumerate(sentence_list):
                            for mid, morph in enumerate(chunk.morphs):
                                print(morph.midasi, end=" ", file=out)
                    print("", file=out)



if __name__ == '__main__':
    #print(makelist_retty())
    
    #data = makelist_retty(datafile="./resources/Rc_shaped_random.csv")
    #makedumps_retty(data, begin=3600, num=100, dirname="dumptest_retty_shuffle", lines_split=True, debug=False)
    #data = makelist_retty(datafile="./resources/Rc_shaped.csv")
    #makedumps_retty(data, begin=5200, num=5000, dirname="dump_retty", lines_split=True, debug=False)
    #checkdump("dumptest", 0)
    #analyze_dump(36,1, 'dumptest_retty_shuffle', "testout2", separate_part=False)
    #l = [i for i in range(0, 36)]+[i for i in range(37, 44)]+[i for i in range(45, 84)]+[i for i in range(85, 100)]
    #l = [i for i in range(0,200)]
    #analyze_dump_fromlist(l, 'dump_retty', "retty0123-0-19999.csv", separate_part=True, case=[1,0,0])

    #data = makelist_tabelog("./resources/T_comment_目黒区.csv")
    #makedumps_tabelog(data, 0, 100, dirname="dumptest_tabelog", lines_split=True, debug=False)
    #makedump_tabelog(data, 0, 25, dirname="dumptest_tabelog", lines_split=True, debug=False)
    #analyze_dump(0, 1, 'dumptest_tabelog', "tabelog_test0-1.csv")
    #a = makelist_retty()[4][2]
    #print(a)
    #print(type(a))
    #a = review_processing(a)
    #print(a)
    #comment_list = get_fromdump("dumptest_retty", 3)
    #print(knp_analyze_from_commentlist_adj(comment_list, visualize=False))
    #c = get_fromdump("dump_tabelog", 102)

    #knp_analyze_from_commentlist_adj(c)
    #knp_analyze_from_commentlist(c, print_result=True, visualize=False)
    wakachi(0, 20000, "dump_retty", "testout")