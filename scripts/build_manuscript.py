#!/usr/bin/env python3
"""Public edition of the evidence-driven paper (2026-11-03).
Public-reader prose and reproduction scope revised; observations unchanged.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import json,pathlib
from integrity import verify_evidence
B=pathlib.Path(__file__).resolve().parents[1];E=B/'evidence'
verify_evidence(E)
def load(f):return json.loads((E/f).read_text(encoding="utf-8"))
S=load('experiment-summary.json');A=S['arms'];T=load('official-solar-term-comparison.json')['summary'];R=load('runtime.json')
blocks=[]
def h(t):blocks.append({'type':'h1','text':t})
def sub(t):blocks.append({'type':'h2','text':t})
def p(t):blocks.append({'type':'p','text':t})
def small(t):blocks.append({'type':'small','text':t})
def table(c,heads,rows,ratios=None,note=None):blocks.append({'type':'table','caption':c,'headers':heads,'rows':rows,'ratios':ratios,'note':note})
def equation(t):blocks.append({'type':'equation','text':t})
def pct(n,d):return f'{100*n/d:.1f}%'
abstract=(f'규칙 기반 계산과 언어모델을 분리하더라도 계산 자료의 오류와 입력 불확실성이 사라지는 것은 아니다. 본 연구는 로컬 사주 프로그램 ollamasaju를 대상으로 역법 자료, 계산 정책, 구조화된 사실 전달을 분리하여 평가한다. 한국천문연구원 확정판 역서와 비교한 2025·2026년 48절기의 내장 시각은 분 단위에서 모두 불일치하였고 평균 절대 편차는 {T["mean_absolute_minutes"]:.2f}분이었다. 반면 음력 월초 25개의 양방향 날짜 변환과 정오 일진은 모두 일치하였다. 시간 미상 분석에서는 네 날짜의 5,760개 분 단위 입력을 열거하여, 시주뿐 아니라 일주 및 입춘일의 년·월주도 단일값으로 확정할 수 없음을 확인하였다. 로컬 gemma4:26b-mlx에 22개 합성 사례를 세 조건·두 회차로 제시한 132회 실험에서 네 필드 전체의 구현 기준 일치 응답은 모델 단독 {A["A"]["exact"]}/44, 텍스트 근거 {A["B"]["exact"]}/44, JSON 근거 {A["C"]["exact"]}/44였다. 이 결과는 제한된 구조화 출력의 전달 충실도이며 자유로운 해석문의 품질이나 사주의 예측 타당성을 뜻하지 않는다. 사례 연구는 외부 정답 검증, 불확실성 전파, 출력 계약 검증을 별개 계층으로 설계할 필요성을 보여준다.')
h('1  서론')
p('언어모델이 자연스럽게 설명하는 능력과 정확한 계산 결과를 보존하는 능력은 같은 성질이 아니다. 생년월일시를 입력받는 사주 소프트웨어는 양력·음력 변환, 윤달 식별, 절기 경계, 일자 전환, 지역 시각 보정처럼 명시적인 계산 절차를 거친다. 그 결과를 언어모델에 제공하면 계산과 문장 생성을 분리할 수 있다. 그러나 이 구조는 계산 결과가 옳다는 전제와, 제공된 결과가 출력에서 유지된다는 전제를 동시에 필요로 한다. 한쪽의 성공만으로 전체 시스템의 정확성을 주장할 수는 없다.')
p('본 연구의 대상인 ollamasaju는 Python 만세력 엔진과 SQLite 역법 자료로 명식을 계산하고, 그 결과를 로컬 언어모델에 전달하는 터미널 응용 프로그램이다. 2026년 11월 3일의 구현 스냅샷을 읽기 전용으로 감사하고 인물과 연결되지 않은 합성 입력으로 검사하였다. 연구의 목적은 사주 해석의 실증적 효용을 입증하는 것이 아니라, 규칙과 언어모델이 만나는 인터페이스에서 어떤 사실과 불확실성이 유지되거나 유실되는지 밝히는 것이다.')
p('연구 질문은 세 가지다. RQ1: 내장 역법 자료와 입력 처리 동작은 외부 자료 및 동치 관계를 만족하는가? RQ2: 출생시각이 없을 때 확정할 수 없는 범위가 시주 이외의 필드로 전파되는가? RQ3: 동일 로컬 모델에서 계산 근거를 제공하는 방식에 따라 네 개 필드의 전달 충실도와 반복 일치도가 어떻게 달라지는가? 세 질문의 평가 기준은 서로 다르며, 한 지표의 결과를 다른 지표의 증거로 대체하지 않는다.')
p('기여는 새로운 신경망 구조가 아니라 검증 가능한 사례와 평가 분해에 있다. 첫째, 확정판 역서에 근거한 시각·달력 대조와 대상 구현의 실패 사례를 제공한다. 둘째, 고정된 정책 아래 가능한 출생 분을 열거하여 불확실성의 범위를 측정한다. 셋째, 모든 요청과 실패를 보존한 로컬 비교 실험을 수행한다. 이러한 기여는 하나의 엔진·자료 스냅샷·모델·장비에 한정되며 일반적인 우월성이나 최초성을 주장하지 않는다.')
h('2  관련 연구와 평가의 관점')
sub('2.1  계산의 외부화와 언어모델의 도구 사용')
p('Transformer는 어텐션을 중심으로 한 시퀀스 처리 구조를 제시하였다[1]. 그러나 해당 구조 자체가 특정 역법의 계산 정확성을 보장하지는 않는다. PAL은 언어모델이 문제를 프로그램으로 표현하고 실행기가 계산을 담당하는 방식을 연구하였으며[2], Program of Thoughts는 수치 계산을 언어모델의 추론과 분리하여 외부 프로그램 실행에 맡기는 접근을 제안하였다[3]. 본 연구의 시스템은 모델이 계산 코드를 생성하는 방식이 아니라 이미 구현된 고정 엔진의 출력을 문맥으로 제공한다는 차이가 있다.')
p('Toolformer와 ReAct는 외부 도구 호출 또는 추론과 행동의 결합을 다루었다[4,5]. 이러한 선행연구는 모델 내부 지식만으로 과업을 처리할 필요가 없음을 보여주지만, 도구 자체의 입력 처리나 데이터 품질을 평가하는 일을 대신하지 않는다. 따라서 도구 사용의 유무, 도구의 정확성, 도구 출력에 대한 모델의 충실도를 별도 축으로 다루어야 한다.')
sub('2.2  사실성, 충실도, 그리고 도메인 선행 산출물')
p('Maynez 등의 연구는 생성문이 입력 자료에 충실한지와 사실에 부합하는지를 구분하여 평가하였다[6]. FActScore는 장문 응답을 원자적 사실로 나누어 근거의 지지 여부를 분석하였다[7]. 본 연구는 그 구분을 참고하되 장문의 모든 주장을 추출하지 않는다. 년주·월주·일주·시주라는 네 개의 사전 정의된 필드만 평가하므로, 여기서 계산한 일치율을 FActScore 점수나 자연어 환각률로 부르지 않는다.')
p('사주 분야에서도 결정론적 역법 계산과 언어모델을 결합한 공개 산출물이 존재한다. Nemotron-Personas-Korea-Saju의 공개 데이터셋 설명에는 역법 계산, 로컬 추론 및 다층 검증이 기술되어 있다[8]. 이는 동료 심사를 거친 성능 검증과 구별해야 하지만, 계산과 설명을 분리하거나 검증기를 추가한 사실만으로 신규성을 주장할 수 없다는 근거가 된다. 본 사례의 초점은 외부 확정 자료 대조, 시간 미상 전파, 동일 정보의 입력 표현 비교, 전체 시도 분모의 보존이다.')
h('3  대상 시스템과 검증 방법')
sub('3.1  대상 시스템과 식별 가능한 실행 환경')
p('대상 시스템은 zsh 실행기, Python CLI, Python 만세력 엔진 및 SQLite 역법 DB, 로컬 모델 호출의 순서로 구성된다. CLI는 인자가 없으면 대화 모드로 진입한다. 감사 당시 사용한 구성 요소의 SHA-256과 기본 정책은 공개 자료의 evidence/public-source-provenance.json에 기록하였다[11]. 이 식별자는 평가에 사용한 구현을 구별하기 위한 것이며, 공개 저장소에 엔진 소스나 역법 DB가 포함되어 있음을 뜻하지 않는다. 본 연구는 서버 응용 프로그램이나 다른 언어로 구현된 별도 엔진을 함께 평가하지 않았다.')
p('대상 CLI의 기본 모델 태그는 gemma4:26b-mlx이고 요청 경로는 루프백 주소의 /api/chat이다. /api/show가 보고한 매개변수 수는 26,225,562,962개, 양자화 표시는 nvfp4였으며 모델 목록의 실행기는 mlx였다. 이는 런타임이 보고한 메타데이터로, 가중치 전체를 독립적으로 분석한 결과는 아니다. 모델 digest와 실행 환경은 evidence/runtime.json에, 요청 옵션은 동결된 요청 자료에 기록하였다. 원격 제공자를 나타내는 모델 태그나 설정은 실험 대상에서 제외하였다.')
blocks.append({'type':'architecture','caption':'그림 1. 평가 계층의 분리. 외부 역서 대조는 계산 계층을 검사하고, A·B·C 비교는 네 필드의 전달을 검사한다. D는 C의 동일 출력을 검증하며 새로운 모델 호출이나 오류 값의 자동 수정을 수행하지 않는다.'})
table('표 1. 측정 환경과 요청 조건', ['항목','기록'],[
 ['장비','Apple M5 Pro · '+f'{R["memory_bytes"]/(1024**3):.0f} GiB 통합 메모리'],['운영체제',R['platform']],['로컬 런타임','Ollama API version '+R['version']['version']+' · mlx'],['모델 태그','gemma4:26b-mlx'],['모델 digest',R['model']['digest'][:32]+'\n'+R['model']['digest'][32:]],['통제 실험 옵션','temperature=0.2, num_ctx=16384, num_predict=256, think=false, stream=false'],['회차별 요청 seed','20261103, 20261104'],['실행 순서','고정 난수로 132개 요청을 섞어 순차 실행'],['동시 호출','호스트 내 공유 파일 잠금으로 순차 실행'],['네트워크 대상','모델 호출은 127.0.0.1:11434만 허용']],[1,3],note='위 옵션은 통제 실험 설정이다. 대상 CLI는 num_ctx만 지정하며, 감사 시 모델 기본 temperature는 1이었다. 실험 결과를 생산 프롬프트 전체의 성능으로 일반화하지 않는다. seed를 요청했지만 서버 구현의 난수 상태까지 독립 검증하지는 않았다.')
sub('3.2  외부 자료와 순환 검증의 방지')
p('외부 기준은 한국천문연구원의 『2025 역서』와 『2026 역서』 확정판 8쪽이다[9,10]. 각 문헌의 판권과 발행일, PDF 원문 주소, 파일 SHA-256을 기록하고 표 이미지와 텍스트 추출 결과를 대조하였다. 잠정 월력 자료나 구현과 같은 계보의 데이터베이스를 독립 정답으로 사용하지 않았다. 수집한 표는 2025·2026년 각 24절기의 한국 표준시 시각과 두 해의 음력 월초 25개다.')
p('절기 비교에서는 내장 DB 시각에서 공식 표 시각을 뺀 분 차이를 계산한다. 공식 표의 정밀도는 분 단위이므로 초 단위의 경계 동작을 단정하지 않는다. 입춘 전환 동작은 공표된 분의 1분 전과 1분 후를 주 비교로 삼고, 정확히 같은 분의 결과는 선택한 분 해상도 정책의 부가 관측으로 보관한다. 역서의 천문 시각은 사주 학파의 자시 처리, 진태양시 채택 여부, 대운 산법을 유일하게 정하는 자료가 아니다.')
equation('시각 편차 = 내장 DB 시각 - 공식 역서 시각')
p('음력 월초 검사는 공식 양력 날짜에서 음력 날짜를 구한 경우, 공식 음력 날짜에서 양력 날짜를 구한 경우, 해당 양력 날짜의 정오 일진을 각각 비교한다. 세 검사는 같은 25개 날짜를 재사용하므로 75개의 독립 표본으로 합산하지 않는다. 전체 역법의 정확도나 모든 윤달 경계를 평가한 것으로 해석하지도 않는다.')
sub('3.3  입력 동치와 시간 미상')
p('합성 입력 감사에는 정상 날짜, 윤일, 잘못된 날짜, 입춘 부근, 자시 전환, 야자시 옵션, 서머타임 옵션, 음력 윤달과 진태양시 조합을 포함하였다. 동치 검사는 같은 출생 사건을 양력과 음력으로 표현했을 때, 동일한 보정 정책 아래 같은 명식을 반환하는지를 확인한다. 잘못된 윤달을 다른 날짜로 조용히 대체하는 동작은 계산 성공과 구별하여 입력 유효성 문제로 분류한다.')
p('출생시각 미상 분석에서는 날짜와 정책을 고정하고 00:00부터 23:59까지 1,440개의 입력을 대상 엔진에 전달한다. 필드 f의 후보 집합 V_f는 이들 입력에서 얻은 서로 다른 결과의 집합이다. 후보가 하나면 해당 구현과 정책 아래 안정적이며, 둘 이상이면 단일값을 확정할 수 없다. 이는 엔진 내부 불확실성 분석이며 외부 역법 기준의 정답을 새로 만들어 내는 절차가 아니다.')
equation('V(f) = { 엔진(f, 날짜, 분, 정책) : 분 = 0, …, 1439 }')
p('평가 대상 날짜는 1990-05-15, 2000-02-29, 2025-02-03, 2026-02-04의 네 날이다. 년·월·일주에서 후보가 여러 개이면 ambiguous와 null을 사용한다. 시각이 입력되지 않은 시주는 unknown과 null로 표현한다. possible 값의 개수나 각 값이 등장한 분 수를 출생시각의 확률 또는 신뢰도로 해석하지 않는다. 이러한 상태 표시는 연구용 전달 규약이며 대상 CLI에 이미 구현되어 있다고 주장하지 않는다.')
sub('3.4  통제된 모델 비교')
p('24개 감사 입력 중 유효하지 않은 양력 날짜 C05와 유효하지 않은 윤달 요청 C23을 모델 호출 전에 제외했다. C05는 엔진이 거부했으며 C23은 엔진이 평달로 대체하는 문제가 관측되었기 때문이다. 두 사례는 입력 감사 결과에 그대로 남긴다. 나머지 22개를 7개 사례 가족으로 묶어 세 조건에 두 번씩 제시하였다. 동일 날짜의 경계 전후 및 회차 반복은 독립 표본으로 취급하지 않는다.')
table('표 2. 실험 조건과 정보의 차이', ['조건','모델에 제공하는 정보','출력 및 평가'],[
 ['A','생년월일시와 정책, 계산 근거 없음','공통 네 필드 JSON'],['B','A의 입력 + 네 필드 값·상태를 평문으로 제공','공통 네 필드 JSON'],['C','A의 입력 + B와 같은 값·상태를 JSON으로 제공','공통 네 필드 JSON'],['D','C가 이미 만든 정확히 같은 응답','모두 일치하면 그대로 전달, 아니면 전체 보류']],[.55,2.1,1.6],note='B와 C의 차이는 근거의 직렬화 형식이다. B·C 모두 같은 불확실성 상태와 출력 규약을 제공한다. D에는 별도의 모델 생성이 없으며 정답 보충, 재생성 또는 값 수정이 없다.')
p('모든 생성 조건은 year, month, day, hour를 최상위 키로 갖는 동일한 JSON 출력을 요청한다. 각 필드는 status와 value로 구성된다. status는 known, ambiguous, unknown 중 하나이며, known일 때만 두 글자 한자 간지를 허용하고 나머지 상태의 value는 null이다. 지시문은 운세나 성격 해석을 요청하지 않는다. 이 설정은 계산 결과가 긴 해석문으로 확장되기 전의 최소 전달 인터페이스를 분리해 측정하기 위한 것이다.')
p('B와 C의 기준 값은 감사 대상 엔진의 결과이며, 시간 미상 사례에는 앞의 후보 집합에서 도출한 상태를 적용한다. 따라서 일치율의 기준은 구현에 대한 충실도다. 엔진 시각이 공식 역서와 다른 구간에서도 엔진 값을 그대로 보존하면 이 지표에서는 일치로 집계된다. A의 낮은 일치율 또한 모든 사주 규약에서의 보편적인 오답률을 뜻하지 않으며, 서로 다른 정책이나 외부 계산값과의 불일치가 포함될 수 있다.')
p('요청 집합, 기준 값, 조건, 회차, 순서를 첫 실험 호출 전에 파일로 고정하고 해시를 기록했다. 이는 로컬 실험 동결 기록이며 외부 기관에 사전 등록한 연구는 아니다. 일반 JSON 한 건으로 워밍업한 뒤 합성 사례의 요청을 실행했다. 원시 응답, 예외, 종료 사유, 잠금 대기시간과 요청 벽시계를 모두 남겼다. 응답이 잘못되거나 실패해도 같은 시도를 자동 재생성하지 않았다.')
sub('3.5  지표와 분석 단위')
p('응답 전체 일치는 스키마와 네 필드의 상태·값이 기준과 모두 같을 때만 인정한다. 필드 일치율의 분모는 조건별 모든 시도에 필요한 필드 수이다. 형식 오류나 누락이 있으면 해당 필드는 0점이며, 성공한 응답만 골라 분모를 줄이지 않는다. 시간 미상 보존 지표는 기준에서 ambiguous 또는 unknown인 필드의 상태와 null이 모두 유지된 비율이다. 같은 회차의 같은 사례를 조건 간에 대응시켜 비교한다.')
equation('필드 일치율 = 일치한 필수 필드 수 / (전체 시도 수 × 4)')
p('D는 C의 JSON 객체가 참조 필드와 완전히 같을 때만 통과시키는 결정론적 계약 검사다. 따라서 통과한 객체가 그 참조와 일치한다는 것은 설계상 성질이며 학습된 검증기의 독립적인 정확도 결과가 아니다. D의 실질적인 관측치는 전달률과 보류율이다. 전체 보류는 네 필드 모두 미전달로 계산한다. 스키마 밖의 자연어 의미, 공식 역법의 옳고 그름, 현실 세계의 예측은 이 검사로 판정할 수 없다.')
p('22개 사례는 오류를 드러내기 위한 목적 표집이며 모집단에서 무작위로 추출한 표본이 아니다. 결과는 사례별·조건별 개수와 기술통계로 제시한다. 작은 표본과 가족 내 의존성, 두 회차뿐인 반복을 고려하여 모집단 신뢰구간이나 유의확률을 보고하지 않는다. 반복 일치도는 두 회차의 파싱된 전체 객체가 같은 사례 수이며, 매번 같은 결과가 나왔다는 사실과 결과가 옳다는 사실을 분리한다.')
h('4  결과')
sub('4.1  독립 역서 대조')
table('표 3. 외부 기준과의 대조 결과', ['검사','대상','일치 / 전체','해석'],[
 ['절기 시각','2025·2026년 각 24절기','0 / 48','분 단위 동일 여부'],['절기 날짜','같은 48절기','46 / 48','시각을 제외한 날짜'],['음력 → 양력','공식 음력 월초','25 / 25','정상 월초의 날짜'],['양력 → 음력','같은 월초','25 / 25','윤달 여부 포함'],['정오 일진','같은 월초','25 / 25','달력 일진 비교'],['입춘 전후 년·월주','각 해 공식 시각 ±1분','2 / 4','선언한 입춘 전환 정책']],[1.2,1.35,.85,1.35],note='표의 행은 서로 다른 척도이며 독립된 표본으로 합산하지 않는다. 입춘 정확히 같은 분의 두 결과는 보조 기록이며 주 비교에서 제외하였다.')
p(f'48개 시각의 평균 절대 편차는 {T["mean_absolute_minutes"]:.2f}분, 절대 편차 중앙값은 {T["median_absolute_minutes"]:.0f}분, 최대는 {T["max_absolute_minutes"]:.0f}분이었다. 부호 있는 차이는 -27분부터 +35분까지였으므로 하나의 고정된 시간대 오프셋만으로 설명되지는 않는다. 본 연구는 해당 내장 자료의 생성 알고리즘까지 역추적하여 오차 원인을 확정하지는 않았다. 따라서 결과는 이 DB 스냅샷과 공표 역서 사이의 편차로 기술한다.')
table('표 4. 실제 동작에 영향을 주는 절기 차이', ['항목','내장 DB · KST','공식 역서 · KST','DB-공식'],[
 ['2025 입춘','02-03 22:49','02-03 23:10','-21분'],['2026 입춘','02-04 04:38','02-04 05:02','-24분'],['2025 동지','12-21 23:44','12-22 00:03','-19분'],['2026 백로','09-08 00:05','09-07 23:41','+24분']],[1,1.35,1.35,.85])
p('2025년 23:09와 2026년 05:01은 각각 공식 입춘 시각의 1분 전이다. 그러나 대상 엔진은 이미 새 년주와 인월의 월주를 반환했다. 공식 시각 1분 후의 두 입력은 선언한 전환 정책과 일치했다. 이런 경계 사례에서는 모델이 엔진 출력을 정확히 복사하더라도 외부 시각 기준의 오류가 사라지지 않는다. 반대로 정상 월초 검사 25개가 일치했다는 결과는 해당 날짜 변환 기능에 한정된 긍정적 증거다.')
sub('4.2  시각 미상의 전파와 입력 처리 실패')
table('표 5. 1,440분 열거에서 관측된 필드별 서로 다른 값의 수', ['고정 날짜','년주','월주','일주','시주'],[
 ['1990-05-15','1','1','2','13'],['2000-02-29','1','1','2','13'],['2025-02-03','2','2','2','13'],['2026-02-04','2','2','2','13']],[2,1,1,1,1],note='총 5,760분의 실제 계산 결과다. 시주 13개는 12지지뿐 아니라 일간이 바뀐 뒤의 자시 조합을 구별한 수다. 후보 수는 정확도나 확률이 아니다.')
p('기본 정책은 한국시각 30분 보정과 정자시 처리를 사용하므로 입력 시계의 23:30에 일주가 다음 날로 전환된다. 네 날짜 모두 00:00–23:29의 1,410분과 23:30–23:59의 30분에서 일주가 달랐다. 평일이라도 출생시각을 전혀 모르면 일주를 하나로 확정할 수 없는 이유다. 입춘일에는 년주와 월주까지 두 개의 후보가 존재했다. 현재 프로그램은 시각 미상에서 시주를 비우지만 년·월·일주에 같은 수준의 불확실성을 표시하지 않는다.')
p('추가 입력 감사에서는 존재하지 않는 음력 2025년 윤1월 1일이 평달 1월 1일로 대체되었고, 반환된 음력 정보에는 leap=true가 남았다. 이는 입력을 거부한 경우와 의미가 다르다. 양력 1900-02-29는 거부되었으므로 두 종류의 유효하지 않은 입력에 대한 처리가 일관되지 않았다. 이 결과를 24개 합성 입력 중 23건이 결과를 반환했다는 실행 수치와 묶어 정확도로 제시하지 않는다.')
p('또 다른 동치 검사에서는 음력 2020년 윤4월 1일 00:10과 이에 대응하는 양력 2020-05-23 00:10에 동일한 진태양시 옵션을 주었다. 두 입력의 일주·시주는 각각 丁卯·庚子와 丙寅·戊子로 달랐다. 대상 구현은 음력 날짜를 양력으로 바꾸기 전에 입력 연·월·일에 시각 보정을 적용한다. 이 순서와 날짜 경계의 상호작용을 동치 실패로 관측하였다. 보고된 결과는 교정 전의 스냅샷에 대한 감사 결과이며 수정된 엔진의 성능 평가가 아니다.')
p('시간 미상의 정밀 대운 시작 값은 별도의 누락 처리 없이 자정 입력과 같았다. 예를 들어 1990-05-15의 미상 입력과 00:00 입력은 모두 7.45년을 반환했다. 이 값은 실제 출생시각에 대해 입증된 정밀도가 아니라 내부 기본값의 결과다. 생성 단계에 전달하기 전에 가정과 미상을 분리하지 않으면, 모델은 이러한 수치를 확정된 사실로 받아들일 수 있다.')
sub('4.3  네 필드 전달 실험')
rows=[]
for arm,name in [('A','A · 모델 단독'),('B','B · 텍스트 근거'),('C','C · JSON 근거')]:
 x=A[arm];rows.append([name,f'{x["exact"]}/44',f'{x["fields_correct"]}/176',f'{x["uncertain_correct"]}/{x["uncertain_total"]}',f'{x["repeat_exact_object_agreement"]}/22'])
table('표 6. 조건별 구현 기준 충실도와 반복 일치도', ['조건','전체 응답','필수 필드','미상·모호 필드','회차 간 객체 일치'],rows,[1.5,1,1,1.2,1.2],note='전체 응답과 필수 필드의 분모는 각각 44와 176이다. 미상·모호 필드는 조건별 20개다. 회차 간 객체 일치는 두 번의 결과가 같은지를 나타내며 정답 여부와 다르다.')
p(f'A의 전체 응답 일치는 {A["A"]["exact"]}/44({pct(A["A"]["exact"],44)}), B는 {A["B"]["exact"]}/44({pct(A["B"]["exact"],44)}), C는 {A["C"]["exact"]}/44({pct(A["C"]["exact"],44)})였다. 필드 단위 일치는 각각 {A["A"]["fields_correct"]}/176, {A["B"]["fields_correct"]}/176, {A["C"]["fields_correct"]}/176이었다. 이 차이는 이 사례 집합에서 계산 사실을 문맥으로 제공했을 때의 전달 동작을 보여준다. 모델 단독 조건과 근거 제공 조건의 차이를 계산 엔진 전체의 외부 정확도 향상으로 읽어서는 안 된다.')
blocks.append({'type':'bars','caption':'그림 2. 전체 시도를 분모로 한 필수 필드 전달 일치 개수. B와 C에 제공된 사실 및 불확실성 정보는 같으며, 막대는 구현 기준과의 일치를 나타낸다. 공식 역서의 독립 정확도는 표 3에서 별도로 평가하였다.','values':[(k,A[k]['fields_correct']) for k in ['A','B','C']],'total':176})
p(f'텍스트 근거 B와 JSON 근거 C는 모두 {A["B"]["schema_pass"]}/44 및 {A["C"]["schema_pass"]}/44의 스키마 준수 응답을 생성했다. 이번 결과만으로 JSON이 평문보다 우월하다는 일반 결론을 내릴 수 없다. 값과 상태가 네 필드로 명확히 한정되고 출력도 짧은 과업에서는 평문 역시 충분한 전달 통로가 될 수 있다. 긴 문맥, 자유로운 해석, 상충하는 지시, 추가 질문 및 누적 대화에서 같은 결과가 유지되는지는 측정하지 않았다.')
rows=[]
for arm in ['A','B','C']:
 x=A[arm];rows.append([arm,f'{x["parse_pass"]}/44',str(x['errors']),str(x['truncated']),f'{x["wall_median_seconds"]:.2f}',f'{x["wall_min_seconds"]:.2f}–{x["wall_max_seconds"]:.2f}'])
table('표 7. 응답 형식과 요청 벽시계', ['조건','JSON 파싱','API 오류','길이 종료','중앙값(초)','범위(초)'],rows,[.6,1,.9,.9,1.2,1.3],note='잠금 획득 후 HTTP 요청부터 응답 수신까지의 벽시계다. 최초 워밍업과 공용 잠금 대기는 제외한다. 장비의 다른 부하·열 상태를 통제한 전용 성능 벤치마크는 아니며 속도의 인과적 우열을 주장하지 않는다.')
table('표 8. C 조건에서 확정값을 만들어 낸 세 응답', ['실행 ID','기준 상태','실제 변경','D 처리'],[
 ['C09_C_R1','년·월·일 ambiguous','乙巳 · 戊寅 · 庚午로 확정','보류'],['C09_C_R2','년·월·일 ambiguous','乙巳 · 戊寅 · 丙辰로 확정','보류'],['C13_C_R2','년 ambiguous','丙午로 확정','보류']],[1.05,1.2,1.65,.65],note='세 응답 모두 JSON 스키마는 통과했고 시주는 unknown을 유지했다. 구문 유효성과 불확실성 보존은 별개다. C09는 2025년 입춘일, C13은 2026년 입춘일의 시간 미상 입력이다.')
p('C의 세 불일치 응답은 모두 시간 미상 입춘 사례에서 발생했다. 기준은 ambiguous와 null이었으나 모델이 총 7개 필드를 known과 구체적인 간지로 바꾸었다. 두 회차의 C09에서는 일주 값마저 서로 달랐다. 짧은 구조화 입력과 올바른 JSON 형식만으로 불확실성이 보존되는 것은 아니며, 이번 사례에서는 텍스트 근거 B가 같은 정보에 대해 더 높은 관측 일치를 보였다.')
p('A의 JSON 파싱 실패 11건은 모두 응답 전체를 Markdown 코드 펜스로 감싼 경우였다. 형식과 내용의 영향을 구별하기 위해 실험 후 바깥 코드 펜스 한 겹만 제거하는 민감도 분석을 추가했다. A의 필드 일치는 59/176에서 78/176으로 바뀌었으나 전체 응답 일치는 여전히 0/44였다. B와 C는 변하지 않았다. 이 추가 분석은 사후 기술 분석이며 주 분석의 사전 고정 분모나 채점 규칙을 변경하지 않았다.')
p(f'D는 C의 {A["D"]["n"]}개 응답 중 {A["D"]["delivered"]}개를 그대로 전달하고 {A["D"]["abstained"]}개를 보류했다. 추가 모델 호출은 0회다. 네 필드가 모두 참조와 일치하는 경우만 허용하므로 통과 집합의 일치율은 검사 정의에 따른 결과다. 별도의 176개 합성 계약 검사에서는 정상 객체 22개와 변조 객체 154개를 구분하였다. 이 검사는 참조 값 변경, 거짓 확정, 누락 및 불필요한 키를 탐지하는 계약 동작을 확인하며 자연어 의미 검증 성능을 대체하지 않는다.')
p('D의 전달률은 41/44(93.2%)였다. 전체 보류를 미전달로 계산하면 전달된 일치 필드는 164/176으로, C의 169/176보다 5개 적다. 검증은 C의 잘못된 7개 필드가 노출되는 것을 막는 대신 같은 응답 안에서 올바르던 5개 필드도 함께 보류했다. 이 가용성 비용을 제외하고 통과 결과만의 일치율을 강조해서는 안 된다.')
h('5  논의')
sub('5.1  높은 충실도가 잘못된 계산을 보존할 수 있다')
p('외부 기준 정확성과 제공된 사실에 대한 충실도는 서로 보완적이다. 계산 엔진의 입춘 시각이 이른 경우, 정확히 그 년주와 월주를 전달하는 모델은 높은 충실도를 얻을 수 있다. 그러나 외부 역서 기준에서 그 출생 사건의 명식이 맞아지는 것은 아니다. 사용자가 보는 문장이 유창할수록 이 구분은 가려질 수 있다. 따라서 시스템 설명이나 평가 결과에는 무엇을 정답으로 삼았는지가 반드시 포함되어야 한다.')
p('이번 사례에서 정상 월초 변환의 성공과 절기 시각의 실패가 함께 나타난 점도 중요하다. 엔진 전체를 한 개의 정확도 숫자로 표현하면 구성 요소별 품질 차이를 숨긴다. 날짜 변환, 분 단위 절입, 입력 유효성, 진태양시 계산 순서, 결과 형식화를 각각 검사하는 편이 실제 결함을 찾아내는 데 유용하다. 고정 엔진의 결정론적 동작은 재현성을 제공하지만 그 자체가 정확성의 증명은 아니다.')
sub('5.2  불확실성은 생성 이전의 자료 구조에 있어야 한다')
p('시간이 없다는 사실을 문장으로 한 번 경고하는 것만으로는 년·월·일주나 대운의 숨은 가정을 표현하기 어렵다. 필드별 상태를 유지하면 어떤 값이 안정적인지, 어떤 값이 여러 후보를 갖는지, 어떤 값이 아예 제공되지 않는지 구분할 수 있다. 본 연구의 known·ambiguous·unknown은 그 목적을 위한 작은 계약이다. 실제 서비스에서는 시간대, 경도, 서머타임 적용 여부, 선택한 자시 규칙과 달력 자료의 버전도 함께 보존해야 한다.')
p('다만 후보 집합을 계산하는 엔진 자체가 잘못되어 있으면 불확실성 집합 또한 잘못될 수 있다. 1,440분 전수 계산은 선택한 구현과 정책의 결과를 빠짐없이 관찰하는 방법이지 천문학적 정확성을 보장하는 방법이 아니다. 역법 자료를 갱신하면 후보 집합과 회귀 사례를 다시 계산해야 한다. 또한 분보다 세밀한 입력이나 출생지 변화가 필요한 과업은 다른 격자와 정책 정의를 요구한다.')
sub('5.3  선택적 전달의 장점과 한계')
p('정해진 네 필드에서는 일치 여부를 직접 비교하여 실패 시 보류할 수 있다. 이는 사람이 보게 될 값이 참조와 다른 경우를 차단하지만, 참조 자체가 잘못된 경우에는 동일한 오류를 허용한다. 설명 전체를 보류하는 방식은 오류 노출과 가용성 사이의 교환을 만든다. 이번 C 조건에서는 실제로 3개 응답이 보류되었다. 해당 사례에서의 차단 성공을 임의의 자연어 입력이나 모든 역법 오류를 탐지하는 능력으로 확장할 수 없다.')
p('자유로운 설명문으로 확장하려면 검증 단위를 더 신중하게 설계해야 한다. 필드가 맞더라도 같은 문단에서 다른 간지를 주장하거나 미상 값을 단정할 수 있기 때문이다. 사실 식별자를 붙이는 것만으로 그런 문장까지 검증되지는 않는다. 장문 설명의 사실 추출, 근거 연결, 상충 주장 탐지, 독립 평가자 간 일치도는 이번 연구 범위 밖에 있으며 후속 평가가 필요하다.')
h('6  타당성의 위협과 연구 윤리')
p('내적 타당성의 한계는 첫째, 모델 조건의 기준 값이 감사 대상 구현에서 나왔다는 점이다. 이를 외부 정확도로 오인하지 않도록 두 평가를 분리했다. 둘째, 두 입력 표현은 의미 정보가 같아도 토큰 수와 구문이 다르다. 이는 표현 형식의 특성이며 순수한 의미 효과와 완전히 분리되지 않는다. 셋째, 대상 CLI의 긴 명리 지침과 전체 계산 자료 대신 짧은 통제 지시문을 사용했다. 결과는 기본 채팅 경험 전체를 대표하지 않는다.')
p('구성 타당성의 한계는 네 필드의 정확한 구조화 일치가 사용자의 이해, 문장의 가독성, 상담의 유용성 또는 문화적 해석의 타당성을 측정하지 않는다는 점이다. 형식이 맞는 문장이나 필드가 과학적 예측을 뜻하지도 않는다. 본 연구는 사람의 미래, 성격, 건강, 재정 상태를 예측하는 능력을 실험하지 않았으며 어떤 긍정적 결과도 그러한 능력의 근거로 사용하지 않는다.')
p('외적 타당성은 한 장비, 한 모델 digest, 한 DB 및 엔진 스냅샷, 22개 목적 표집 사례와 두 회차로 제한된다. 7개 가족에 속하는 사례들은 상호 관련되어 있다. 다른 모델 크기, 양자화, 프롬프트 언어, 더 긴 문맥, 다른 학파의 규칙 또는 장기간 운영에서도 결과가 유지된다고 주장하지 않는다. 공식 역서 대조도 두 해와 월초에 국한되므로 과거 전체 기간의 정확도는 별도 검증 대상이다.')
p('재현 자료와 구현 식별자는 공개 저장소에서 제공한다[11,12]. 모든 출생 입력은 합성 사례이며 이용자 로그나 개인의 출생 기록을 수집하지 않았다. 모델 요청은 로컬 루프백 주소로만 전송하였다. 이는 이 실험의 데이터 흐름을 설명할 뿐 운영 환경 전체의 개인정보 보호를 보장하는 결과는 아니다. 공개 패키지는 연구용 원고·분석 코드와 관측 자료를 포함하며, 모델 가중치·역법 DB·상용 서체 파일·역서 원문 PDF는 포함하지 않는다. 외부 자료의 출처와 권리는 별도로 표시하였다.')
p('연구 대상은 저자가 개발·관리하는 소프트웨어이므로 설계 선택과 평가 해석에 이해관계가 존재한다. 이를 드러내고 검토 가능성을 높이기 위해 외부 확정 자료의 출처, 실패 사례, 동결된 전체 요청, 원시 응답과 분석 코드를 공개하였다. 공개된 관측값을 다시 집계하는 절차와 별도 연구자가 엔진·모델을 새로 실행하여 재현하는 절차는 다르다. 이 원고는 독립 연구기관의 재현 또는 동료 심사를 완료한 결과로 제시되지 않는다.')
h('7  결론')
p(f'본 사례 연구는 계산과 언어모델의 역할 분리가 검증의 종착점이 아님을 보여주었다. 내장 절기 시각 48개는 공식 역서와 분 단위에서 일치하지 않았지만, 정상 음력 월초 25개의 날짜 변환은 일치했다. 시간 미상은 시주뿐 아니라 일주와 입춘일의 년·월주로 전파되었다. 통제된 132회 생성에서 근거 제공 조건 B와 C는 각각 {A["B"]["exact"]}/44 및 {A["C"]["exact"]}/44의 전체 필드 일치를 보였으나, 이 결과가 계산 원천의 오류를 정정하는 것은 아니었다.')
p('따라서 규칙 기반 엔진과 언어모델을 결합하는 시스템은 외부 기준에 대한 계산 감사, 입력 가정과 불확실성의 명시, 생성 결과의 전달 계약을 각각 유지해야 한다. 공개된 요청·응답과 분석 도구는 이 세 계층의 판단 근거를 독자가 다시 검토할 수 있게 한다. 다만 보존된 관측값의 재집계가 미배포 엔진이나 모델의 독립 재실행을 대신하지는 않는다. 후속 연구는 역법 자료의 독립적인 교정과 회귀 검사, 더 넓은 경계 입력, 다른 모델 및 자유로운 설명문을 대상으로 확장할 수 있다.')
h('자료·코드 공개와 작성 지원')
small('공개 저장소 https://github.com/mobidicSaju/saju-llm-fact-check 에 연구 원고, 합성 사례, 132개 요청과 원시 응답, 공식 자료의 출처·쪽·해시, 표준 라이브러리 기반 재분석 코드를 제공한다. 원시 응답과 동결 해시는 최초 관측의 바이트를 유지한다. 자체 작성한 원고와 코드에는 Apache License 2.0을 적용하며, 외부 자료와 제3자의 권리 범위는 NOTICE에 구분한다. 원고 구성, 코드 작성 및 교차 점검에는 생성형 AI 보조 도구를 사용하였다. 연구 질문·분석·해석에 대한 책임은 저자에게 있다.')
h('참고문헌')
refs=[
 '[1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin. Attention Is All You Need. Advances in Neural Information Processing Systems 30, 2017. https://arxiv.org/abs/1706.03762',
 '[2] L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig. PAL: Program-aided Language Models. Proceedings of ICML, PMLR 202:10764–10799, 2023. https://proceedings.mlr.press/v202/gao23f.html',
 '[3] W. Chen, X. Ma, X. Wang, and W. W. Cohen. Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks. Transactions on Machine Learning Research, 2023. https://arxiv.org/abs/2211.12588',
 '[4] T. Schick et al. Toolformer: Language Models Can Teach Themselves to Use Tools. Advances in Neural Information Processing Systems 36, 2023. https://proceedings.neurips.cc/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html',
 '[5] S. Yao et al. ReAct: Synergizing Reasoning and Acting in Language Models. International Conference on Learning Representations, 2023. https://arxiv.org/abs/2210.03629',
 '[6] J. Maynez, S. Narayan, B. Bohnet, and R. McDonald. On Faithfulness and Factuality in Abstractive Summarization. Proceedings of ACL, pp. 1906–1919, 2020. doi:10.18653/v1/2020.acl-main.173.',
 '[7] S. Min et al. FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. Proceedings of EMNLP, pp. 12076–12100, 2023. doi:10.18653/v1/2023.emnlp-main.741.',
 '[8] rayraykim. Nemotron-Personas-Korea-Saju: Dataset Card. Hugging Face, commit ae3851f0d4551401df13bd8470f106de4bea30c5, 2026. Public technical artifact; not a peer-reviewed article. https://huggingface.co/datasets/rayraykim/Nemotron-Personas-Korea-Saju/blob/ae3851f0d4551401df13bd8470f106de4bea30c5/README.md (accessed 2026-11-03).',
 '[9] 한국천문연구원. 2025 역서. 2024년 10월 25일 발행. 자료: 8쪽, 판권: 232쪽. https://astro.kasi.re.kr/file/astro_almanac_pdf/20250828102520786.pdf (확인 2026-11-03).',
 '[10] 한국천문연구원. 2026 역서. 2025년 9월 25일 발행. 자료: 8쪽, 판권: 232쪽. https://astro.kasi.re.kr/file/astro_almanac_pdf/20260325110341610.pdf (확인 2026-11-03).',
 '[11] 박성모. ollamasaju 실행 환경과 계산 스냅샷 식별 자료. evidence/public-source-provenance.json 및 evidence/runtime.json, 2026-11-03. https://github.com/mobidicSaju/saju-llm-fact-check',
 '[12] 박성모. 계산과 설명 사이의 사실 보존: 공개 요청·응답 및 재분석 자료. evidence/experiment-protocol.json, experiment-requests.json, experiment-raw.jsonl 및 scripts/reproduce.py, 2026-11-03. https://github.com/mobidicSaju/saju-llm-fact-check'
]
for ref in refs:small(ref)
blocks.append({'type':'page'})
h('부록 A  합성 사례와 재현 절차')
p('모든 사례는 인물과 연결되지 않은 합성 입력이다. 표 A1의 기본값은 양력, 한국시각 보정 사용, 정자시, 진태양시 미사용, 서머타임 보정 사용이다. “미상”은 hour와 minute가 모두 null임을 뜻한다. 같은 가족과 반복 회차를 분리해 새로운 독립 표본으로 세지 않는다. 시간 미상 전수의 네 날짜와 생성 실험의 시간 미상 세 사례는 구별한다.')
case_rows=[]
for row in load('synthetic-cases.json'):
 i=row['input'];date=f'{i["year"]:04}-{i["month"]:02}-{i["day"]:02}';clock='미상' if i['hour'] is None else f'{i["hour"]:02}:{i["minute"]:02}'
 flags=[]
 if i.get('is_lunar'):flags.append('음력 윤달' if i.get('is_leap') else '음력 평달')
 if i.get('use_yaja_si'):flags.append('야자시')
 if i.get('use_korean_time') is False:flags.append('-30분 보정 끔')
 if i.get('apply_dst_correction') is False:flags.append('DST 끔')
 if i.get('use_true_solar_time'):flags.append('진태양시')
 include='감사만' if row['case_id'] in ['C05','C23'] else '감사·생성'
 case_rows.append([row['case_id'],date,clock,', '.join(flags) or '기본',include])
table('표 A1. 고정된 입력 24개와 사용 범위', ['ID','입력 날짜','시각','변경 옵션','범위'],case_rows,[.6,1.25,.7,1.6,1])
sub('A.1  공개 자료를 이용한 재분석')
p('공개 저장소의 최상위 폴더를 기준으로 evidence/에는 관측 자료와 해시 목록이, scripts/에는 재분석 도구가 있다. Python 3.11 이상에서 Windows는 py -3 scripts/reproduce.py, macOS와 Linux는 python3 scripts/reproduce.py로 실행한다. 도구는 파일 해시와 132개 시도 식별자를 검사한 뒤 조건별 채점, 반복 일치도, 계약 검사 및 형식 민감도 결과를 reproduced/에 생성하고 보관된 결과와 대조한다. 패키지 설치, 모델 다운로드, 네트워크 연결은 필요하지 않다.')
p('scripts/reproduce.py는 절기 관측값의 시각 차이, 월초와 입춘 검사의 집계, 미상 시각 후보 집합의 분 단위 합계도 검산한다. 이는 공개된 관측 기록에 대한 산술·일관성 검사다. 역법 엔진을 다시 실행하거나 한국천문연구원의 원문을 새로 전사하는 검사는 수행하지 않는다. 원문 대조에는 evidence/kasi-oracle/source_manifest.json의 출처·판본·쪽·SHA-256을 사용할 수 있다.')
p('모델의 새 추론 및 엔진 계산의 독립 재실행에는 해당 모델, 런타임, 엔진과 DB 스냅샷, 이용 권한이 별도로 필요하다. 이 공개 패키지는 그 파일들을 배포하지 않으며 새 실행을 수행하는 스크립트도 포함하지 않는다. 환경이 같더라도 난수 상태와 런타임 구현에 따라 새 응답은 달라질 수 있다. 기존 원시 기록의 보존과 새 실험의 결과 비교는 구별되어야 한다.')
sub('A.2  네 필드 전달 규약의 전체 핵심 지시')
p('사주 계산 결과의 네 필드를 전달하는 소프트웨어 평가입니다. 운세나 성격을 해석하지 마세요. 출력은 JSON 객체 하나이며 코드 펜스와 부가 설명을 쓰지 마세요. 최상위 키는 year, month, day, hour입니다. 각 필드는 status와 value를 가집니다. status는 known, ambiguous, unknown 중 하나입니다. known은 단일 간지가 확정됨, ambiguous는 주어진 입력과 정책에서 둘 이상의 값이 가능함, unknown은 출생시각 미상으로 시주를 제공하지 않음입니다. known일 때 value는 두 글자 한자 문자열, 나머지는 JSON null입니다. 근거 데이터가 있으면 그대로 전달하고 재계산하지 마세요. 출생시각이 없을 때 시주는 unknown이며, 다른 필드도 시각에 따라 달라진다면 ambiguous입니다. 확률이나 다수결로 단일값을 선택하지 마세요.')
small('위 문단은 읽기 쉽게 필드 설명을 풀어 쓴 규약이다. 공백·JSON 예시·입력 정책을 포함한 실제 요청 전문은 experiment-requests.json에 132건 모두 보존한다. 이 문단의 재입력을 원래 프롬프트의 바이트 단위 재현으로 사용하지 않는다.')
h('부록 B  해석 범위와 증거 파일')
table('표 B1. 주장과 근거 파일의 대응', ['주장 또는 측정','정본 증거 파일'],[
 ['구성 요소·스냅샷 식별 해시','public-source-provenance.json'],['24개 입력·원본 관측 결과','synthetic-cases.json / calendar-case-observations.json'],['5,760분 후보 집합','unknown-time-enumeration.json'],['48절기 독립 비교','official-solar-term-comparison.json'],['25월초 양방향·일진 검사','official-lunar-month-start-checks.json'],['공식 입춘 전후 계산','official-ipchun-engine-checks.json'],['잘못된 윤달·동치 실패','calendar-metamorphic-observations.json'],['모델·장비 메타데이터','runtime.json'],['호출 전 동결','experiment-protocol.json / experiment-frozen-hashes.json'],['모든 요청과 원시 응답','experiment-requests.json / experiment-raw.jsonl'],['재집계 결과·개별 채점','experiment-summary.json / experiment-scored.json'],['합성 계약 검사','validator-fault-injection.json']],[1.25,2.5])
p('표 B1의 증거는 하나의 연구 실행을 문서화한다. 전체 API 시도는 원시 로그에서 확인할 수 있으며 성공한 응답만 추려 보존하지 않았다. 실패 사례는 숨기지 않고 계산 자료, 입력 처리, 미상 상태, 생성 전달의 어느 계층에 속하는지 구분했다. 외부 공식 자료의 전체 원문을 복제하지 않고 출처·판본·쪽·해시와 평가에 필요한 전사값만 기록하였다.')
h('English Abstract')
small('Separating deterministic computation from language generation does not remove errors in the computational source or uncertainty in the input. This case study audits ollamasaju, a local Saju application, and separates calendar correctness from structured fact preservation. Against the published 2025 and 2026 almanacs of the Korea Astronomy and Space Science Institute, all 48 embedded solar-term timestamps differed at minute resolution, with a mean absolute difference of 17.90 minutes. Bidirectional calendar conversion and noon day-cycle labels matched for 25 lunar month starts. Enumerating 5,760 minute-level inputs across four dates showed that missing birth time can affect the day pillar and, on the start-of-spring dates, the year and month pillars. A controlled local experiment used gemma4:26b-mlx on 22 synthetic cases, three conditions, and two repeats, totaling 132 calls. Complete four-field matches against the frozen implementation reference were 0/44 without calculated facts, 44/44 with textual facts, and 41/44 with JSON facts. Three JSON-grounded responses replaced ambiguous values with unsupported certainty. An exact field gate withheld those responses without regeneration. These results concern a finite structured-output task, not free-form explanation quality or the predictive validity of Saju. External source validation, uncertainty propagation, and output-contract checking must be evaluated separately.')
small('Keywords: local language model; calendar verification; factual faithfulness; missing birth time; structured output')
M={'title':['계산과 설명 사이의 사실 보존','로컬 사주 언어모델의 경계 사례 평가'],'english_title':['Preserving Facts between Computation and Explanation','A Boundary-Case Study of a Local Saju Language Model'],'author':'박성모','email':'vividsaebom@gmail.com','date':'2026-11-03','abstract':abstract,'keywords':'로컬 언어모델, 역법 검증, 사실 충실도, 시간 미상, 구조화 출력','blocks':blocks}
def plain_text(document):
    lines = document['title'] + document['english_title']
    lines += [document['author'], document['date'], document['abstract'], document['keywords']]
    for block in document['blocks']:
        if block['type'] == 'page':
            continue
        if block['type'] == 'table':
            lines += [block['caption'], ' | '.join(block['headers'])]
            lines += [' | '.join(str(cell) for cell in row) for row in block['rows']]
            if block.get('note'):
                lines.append(block['note'])
        else:
            lines.append(block.get('text', block.get('caption', '')))
    return '\n\n'.join(lines) + '\n'

(B/'manuscript.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(B/'manuscript.txt').write_text(plain_text(M), encoding='utf-8')
print('manuscript blocks', len(blocks))
