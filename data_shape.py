

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


if __name__ == '__main__':
    reshape_retty_comment()