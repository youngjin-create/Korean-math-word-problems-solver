# %%

from konlpy.tag import Okt, Komoran, Hannanum, Kkma , Mecab
mecab = Mecab()

text = u'들어가신다.'
#fn.pos(text)
print(mecab.pos(text))
# %%
