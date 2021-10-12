# %%

from konlpy.tag import Okt, Komoran, Hannanum, Kkma , Mecab
okt = Mecab()

text = u'석진이는 호석이보다 무겁고 지민이보다 가볍습니다. 남준이는 지민이보다 가볍습니다. 4명 중 가장 무거운 사람은 누구입니까?'
#fn.pos(text)
print(okt.pos(text))
# %%
