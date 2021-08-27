
2021/08/27

1. main.py: problemsheet.json을 읽어서 한 문제식 풀이 호출
2. nl_preprocess.py: 수학 문제 문장 전처리, 단어나 숫자 매핑, 띄어쓰기나 맞춤법 정규화, 형태소 분석(?)

3. nl_to_fr.py: 자연어를 형식표현(formal representation)으로 변환.
일단은 sentence 매칭 기반으로 매치되는 문장을 찾아서 변환
3.1. 가장 유사한 문장을 찾는 알고리즘
3.2. 매칭에 기반해서 표현을 구하는

문제 유형을 먼저 파악
(similarity table을 대회 특화용으로 구성하는 것도 방법? 답을 구하시오. - 계산하시오.)

4. fr_solver.py: formal representaion에서 추론 과정을 거쳐서 답을 계산

3,4는 반복하면서 가장 좋은 매칭과 답을 구할 수 있도록 탐색 진행

