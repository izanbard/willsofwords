import json

with open("profanity1.txt", "r") as fd:
    list1 = [
        x.strip().replace(" ", "").replace("-", " ").upper()
        for x in fd.readlines()
        if x.strip().isascii() and x.strip().isalpha()
    ]
with open("profanity2.txt", "r") as fd:
    list2 = [
        x.strip().replace(" ", "").replace("-", " ").upper()
        for x in fd.readlines()
        if x.strip().isascii() and x.strip().isalpha()
    ]
with open("profanity3.json", "r") as fd:
    list3 = [
        x.strip().replace(" ", "").replace("-", " ").upper() for x in json.loads(fd.read()) if x.isascii() and x.isalpha()
    ]

myset = set(list1 + list2 + list3)

mylist = list(myset)

mylist.sort()

with open("profanity.txt", "w") as fd:
    fd.write("\n".join(mylist))
