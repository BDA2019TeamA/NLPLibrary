

def reshape_retty_comment():
    with open("resources/R_comment_目黒区.csv", "r") as intxt, open("resources/Rc_shaped.csv", "w") as out:
        allstr = intxt.read().split(",https://retty.me/area/")
        for num, review in enumerate(allstr[1:]):
            review_elements = review.split(",")
            url = "https://retty.me/area/"+review_elements[0]
            review = ",".join(review_elements[1:-3])
            storeid = review_elements[-3]
            reviewid = review_elements[-2]
            score, id = review_elements[-1].split("\n")
            if id is "":
                id="64598"
            id = int(id)-1
            assert id==num
            string = ",".join([str(id), url, review, storeid, reviewid, score])
            string = string.replace("\n", "\t")
            print(string, file=out)


def reshape_guru_comment():
    with open("resources/gurunabi_comments.csv", "r") as intxt, open("resources/Gc_shaped.csv", "w") as out:
        allstr = intxt.readlines()
        count = -1
        outstr = str(count)+","
        for i,string in enumerate(allstr):
            if len(string)<20:
                outstr += string
            elif string[0]=='"' and string[8:11]=='","':
                outstr = outstr.replace("\n", "\t")
                print(outstr, file=out)
                count += 1
                outstr = str(count)+","
                outstr += string
            else:
                outstr += string
        outstr = outstr.replace("\n", "\t")
        print(outstr, file=out)


def reshape_tabelog_comment():
    with open("resources/T_comment_目黒区.csv", "r") as intxt, open("resources/Tc_shaped.csv", "w") as out:
        allstr = intxt.readlines()
        outstr = ""
        for string in allstr:
            string = string.strip("\n")
            if len(string)<20:
                outstr += "\t"
                outstr += string
            elif ",https://tabelog.com/" in string[5:35]:
                print(outstr, file=out)
                outstr = string
            else:
                outstr += string
        print(outstr, file=out)


if __name__ == '__main__':
    #reshape_retty_comment()
    reshape_guru_comment()
    #reshape_tabelog_comment()