import pickle
from nlplib_pyknp2 import *
import re
import traceback

def review_processing(review):
    review = re.sub(r"#", "", review)
    review = re.sub(r"\ ", "　", review)
    review = re.sub(r"https?://(.+?)[,\ 　\"\n]", "", review)
    review = re.sub(r"\((.*?)\)", "", review)
    review = review[1:-1]
    return review

def makedump_retty(datas, begin, num, lines_split=False, debug=False):
    f = open("./dumptest/log"+str(begin//100), "w")
    knp = KNP(option = '-tab -anaphora', jumanpp=True)
    result = []
    end = min(begin+num, 64598)
    for i, data in enumerate(datas[begin:begin+num]):
        print(i)
        review = review_processing(data[2])

        comment_list = pyknp_make_commentlist(review, knp, lines_split=lines_split, logfile=f)
        data.append(comment_list)
        result.append(data)
        if debug:
            for j in knp_analyze_from_commentlist(comment_list):
                print(j, file=f)
    f.close()

    with open('./dumptest/knpresult_'+str(begin//100)+'.pickle', 'wb') as f:
        pickle.dump(result, f)
    return result


def makelist_retty():
    datas = []
    with open("R_comment_目黒区.csv") as coms:
        allstr = coms.read().split(",https://retty.me/area/")
        for num, rev in enumerate(allstr[1:]):
            rev_els = rev.split(",")

            url = "https://retty.me/area/"+rev_els[0]
            review = ",".join(rev_els[1:-3])
            storeid = rev_els[-3]
            reviewid = rev_els[-2]
            score, id = rev_els[-1].split("\n")
            if id is "":
                id="64598"
            id = int(id)-1
            assert id==num
            datas.append([id, url, review, storeid, reviewid, score])
    return datas


def makedumps_retty(datas, begin, num, lines_split=False, debug=False):
    assert(num%100==0)
    assert(begin%100==0)
    begin_id = begin // 100

    for i in range(num//100):
        makedump_retty(datas, 100*(begin_id + i), 100, lines_split=lines_split, debug=debug)


def checkdump(dump_id):
    with open('./dumptest/knpresult_'+str(dump_id)+'.pickle', 'rb') as f:
        results = pickle.load(f)
        print(len(results))
        for result in results:
            try:
                knp_analyze_from_commentlist(result[-1], visualize=False)
            except Exception:
                print()
        print(len(results))


def analyze_dump(dump_id_s, num):
    with open("./test.csv","w") as out:
        print("レビューid,動詞or形容詞or名詞,副詞,否定,対象名詞,ノ格,否定", file=out)
        for i in range(dump_id_s, dump_id_s+num):
            with open('./dumptest/knpresult_'+str(i)+'.pickle', 'rb') as f:
                knp_results = pickle.load(f)
                mean = []
                for i, result in enumerate(knp_results):
                    try:
                        analyze_result = knp_analyze_from_commentlist(result[-1], visualize=False)
                        for el in analyze_result:
                            el.insert(0, str(i))
                            mean.append(el)
                    except Exception:
                        print(i, "###error###")
                        sleep(1)
                for m in mean:
                    print(','.join(m), file=out)






if __name__ == '__main__':
    #data = makelist_retty()
    #makedumps_retty(data, 7800, 200, lines_split=True, debug=False)
    #checkdump(36)
    analyze_dump(0,1)