
from buildz.aiclient.skills.file import confx
note=confx.build_note()
fp="./tst.txt"
s = "test"
print(confx.write(s, fp))
print(confx.mkdir("./x"))
print(confx.mkdir("./x"))
