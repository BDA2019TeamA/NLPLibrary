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
    if review[0]=='"':
        review = review[1:]
    if review[-1]=='"':
        review = review[:-1]
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
        for i in range(1, len(allstr)-1, 5):
            rid, CP, url = allstr[i].split(",")[:-1]
            review = allstr[i+2][10:]
            _, service_score, storeid, reviewid, taste, evaluation, drink, env = allstr[i+4].split(",")
            rid = int(rid)
            assert rid==((i-1)//5)
            datas.append([rid, url, review, CP, service_score, storeid, reviewid, taste, evaluation, drink, env])
    return datas


def makedump_retty(datas, begin, num, dirname, lines_split=False, debug=False):
    f = open("./"+dirname+"/log"+str(begin//100), "w")
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
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


def makedump_tabelog(datas, begin, num, dirname, lines_split=False, debug=False):
    f = open("./"+dirname+"/log"+str(begin//100), "w")
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    result = []
    end = min(begin+num, 274)
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


def makedumps_retty(datas, begin, num, dirname, lines_split=False, debug=False):
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_retty(datas, 100*(begin_id + i), 100, dirname=dirname, lines_split=lines_split, debug=debug)

def makedumps_tabelog(datas, begin, num, dirname, lines_split=False, debug=False):
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_tabelog(datas, 100*(begin_id + i), 100, dirname=dirname, lines_split=lines_split, debug=debug)


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




if __name__ == '__main__':
    #print(makelist_retty())
    
    #data = makelist_retty(datafile="./resources/Rc_shaped_random.csv")
    #makedumps_retty(data, begin=0, num=100, dirname="dumptest_retty_shuffle", lines_split=True, debug=False)
    #checkdump("dumptest", 0)
    analyze_dump(0,1, 'dumptest_retty_shuffle', "test1.csv", separate_part=False)
    #l = [i for i in range(0, 36)]+[i for i in range(37, 44)]+[i for i in range(45, 84)]+[i for i in range(85, 100)]
    #analyze_dump_fromlist(l, 'dumptest_retty_shuffle', "retty0112-0-4999_verb.csv", separate_part=True)

    #data = makelist_tabelog("./resources/T_comment_目黒区.csv")
    #makedumps_tabelog(data, 0, 100, dirname="dumptest_tabelog", lines_split=True, debug=False)
    #makedump_tabelog(data, 0, 25, dirname="dumptest_tabelog", lines_split=True, debug=False)
    #analyze_dump(0, 1, 'dumptest_tabelog', "tabelog_test0-1.csv")
    #a = makelist_retty()[4][2]
    #print(a)
    #print(type(a))
    #a = review_processing(a)
    #print(a)
    