# 계산과 설명 사이의 사실 보존

**로컬 사주 언어모델의 경계 사례 평가** — 박성모, 2026-11-03

이 저장소는 역법 계산의 정확성, 출생시각 미상의 전파, 언어모델의 계산 사실 전달을 나누어 평가한 사례 연구를 공개합니다. [전체 원고](manuscript.txt), [구조화된 원고](manuscript.json), 원시 요청·응답과 재분석 코드를 함께 제공합니다. 학술지 게재나 독립 재현이 완료된 논문으로 표시하지 않습니다.

공개 주소: [mobidicSaju/saju-llm-fact-check](https://github.com/mobidicSaju/saju-llm-fact-check)

## 논문 읽기와 편집 파일

**[최종 논문 PDF 읽기·내려받기](paper/PAPER_PUBLIC_A4_INDESIGN.pdf)** — A4 16쪽, 양면 인쇄 8장. InDesign 21.6에서 저장·PDF 내보내기·디스크 재열기를 완료하고 전체 16쪽을 검수했습니다.

- [비교용 조판 기준 PDF — 16쪽](paper/PAPER_PUBLIC_A4.pdf): 전체 페이지 시각 검수와 원고 449항목의 순서 대조를 통과한 조판 기준본입니다.
- [편집용 IDML](paper/PAPER_PUBLIC_A4.idml): 16쪽·794개 독립 Story의 배치형 문서입니다. 원본 윤디자인 서체는 별도 설치가 필요합니다.
- [텍스트 원고](manuscript.txt): 표의 모든 행과 주석을 포함합니다.

[네이티브 INDD](paper/PAPER_PUBLIC_A4.indd)도 함께 제공합니다. 저장·재열기 검사에서 16쪽·794개 Story·승인 서체 4종, 넘친 글자 0·외부 링크 0·프리플라이트 오류 0을 확인했습니다. 네이티브 PDF는 조판 기준본과 16쪽 모두 순서 있는 문자가 일치하며, 페이지 밖의 글자와 시각 검수 결함이 없습니다. PyMuPDF가 설치된 환경에서는 `python3 scripts/verify_paper_pdf.py`로 문자·서체·경계 검사를 다시 실행할 수 있습니다(Windows는 `py -3`). 이 명령은 앱 열기나 사람의 시각 검수를 대신하지 않습니다. [검증 기록](qa/native-validation.json)은 구조 검사·네이티브 검사·전체 페이지 시각 검수를 구분하여 보존합니다.

## 관측 결과

| 평가 | 결과 | 의미와 범위 |
|---|---|---|
| 2025·2026년 공식 역서 48절기 | 분 단위 0/48 일치, 평균 절대 편차 17.90분 | 감사한 DB 스냅샷과 공식 역서의 비교 |
| 음력 월초 25개 | 양방향 변환·정오 일진 각각 25/25 | 같은 25개 날짜를 재사용하므로 75개 독립 표본이 아님 |
| 시각 미상 4일 | 5,760분 열거 | 일주와 입춘일의 년·월주에도 불확실성이 전파됨 |
| 모델 단독 A | 전체 네 필드 0/44 일치 | 아래 모든 모델 지표는 동결된 구현 기준과 비교 |
| 평문 근거 B | 44/44 일치 | 짧은 구조화 출력의 전달 충실도 |
| JSON 근거 C | 41/44 일치 | 불확실한 값을 확정하는 응답 3개 관측 |
| 계약 검사 D | C의 41개 전달, 3개 보류 | 추가 생성·값 수정 없이 동일한 C 출력을 검사 |

모델 실험은 22개 합성 사례 × 3조건 × 2회차 = **132회**입니다. 7개 사례 가족과 경계 전후·반복 응답은 독립 표본이 아닙니다. 한 모델 digest·한 장비·한 엔진/DB 스냅샷을 다룬 목적 표집 사례 연구입니다. 결과를 사주의 예측 타당성, 자유로운 해석문 품질, 전체 역법의 정확도 또는 일반적인 모델 우열로 확장하지 않습니다. 생성 결과가 구현을 충실히 따르는 것과 구현이 외부 기준에서 정확한 것은 별개입니다.

## 추가 모델 호출 없이 재분석하기

Python 3.11 이상과 이 저장소만 필요합니다. 패키지 설치·GPU·모델·역법 DB·네트워크 연결을 사용하지 않습니다. ZIP을 풀거나 저장소를 내려받은 뒤 최상위 폴더에서 실행합니다.

Windows PowerShell:

```powershell
py -3 scripts/reproduce.py
```

macOS 또는 Linux:

```bash
python3 scripts/reproduce.py
```

`reproduced/`에 생성한 채점·요약·계약 검사·형식 민감도 결과 4개를 보관된 결과와 JSON 값 및 바이트 단위로 비교합니다. 명령이 성공하면 `calls: 132`, `exact_responses: {A: 0, B: 44, C: 41}`와 모든 비교의 `true`를 출력합니다. UTF-8과 LF로 기록하므로 생성 파일의 직렬화도 유지됩니다. 원시 `evidence/`는 변경하지 않습니다.

`--check`를 붙이면 임시 폴더에서 검사한 뒤 자동 정리합니다. `--output 경로`로 파생 결과의 위치를 바꿀 수 있습니다. `scripts/build_manuscript.py`는 보관된 수치와 공개판 원고 소스로 `manuscript.json`·`manuscript.txt`를 다시 만듭니다.

## 재현할 수 있는 것과 배포하지 않는 것

| 자료 | 가능한 확인 |
|---|---|
| `experiment-requests.json`, `experiment-raw.jsonl` | 132개 전체 시도·응답·참조·회차·실행 시간 확인 |
| `experiment-frozen-hashes.json` | 최초 호출 전 고정한 입력 4개의 해시 대조 |
| `published-evidence-sha256.json` | 공개한 원본 증거 20개와 파생 provenance 1개의 무결성 대조 |
| `official-*-checks.json`, `official-solar-term-comparison.json` | 관측값에서 달력 지표 재계산 |
| `unknown-time-enumeration.json` | 4일의 필드 후보 및 분 단위 합계 검산 |
| `public-source-provenance.json`, `runtime.json` | 대상 구성 요소·소스/DB 해시·정책·모델 digest·장비 식별 |
| `kasi-oracle/` | 공식 출처·판본·쪽·해시와 평가에 사용한 사실 전사값 확인 |

재분석은 **보존된 관측 기록의 집계와 일관성 확인**입니다. 엔진 재실행, 모델의 새 추론, 공식 역서의 독립 재전사를 수행하지 않습니다. 원본 엔진·SQLite 역법 DB·모델 가중치는 포함하지 않으므로 이 패키지만으로 최초 실험의 모든 실행을 재현할 수 있다고 주장하지 않습니다. 새 추론이 원시 응답과 바이트 단위로 같을 것이라는 보장도 없습니다.

워밍업 기록 `warmup.json`은 본 실험 132회와 구분합니다. 조건 D와 합성 오류주입 검사는 추가 모델 호출이 아닙니다. 실패 또는 불일치 출력을 성공 응답으로 바꾸거나, 성공한 응답만으로 분모를 줄이지 않았습니다.

## 원고와 조판

원고는 `scripts/build_manuscript.py`와 그 생성물 `manuscript.json`·`manuscript.txt`에 있습니다. 텍스트판은 표의 모든 행과 주석을 포함합니다. 조판 소스 `scripts/build_paper.py`는 PyMuPDF와 정당한 이용 권한으로 설치한 윤명조 730/760·윤고딕 740/760을 요구하며, 재분석 도구의 표준 라이브러리만으로 실행되는 범위와 구별합니다. 서체 파일이나 제작자의 로컬 활성화 경로는 배포하지 않습니다. PDF를 다시 조판할 때는 네 서체의 `postscript`·`path`를 담은 로컬 JSON을 저장소 밖에 준비하고 다음처럼 경로를 명시합니다. Windows에서는 `python3`를 `py -3`으로 바꿉니다.

```bash
python3 scripts/build_paper.py --fonts ../fonts.local.json --output paper/PAPER_PUBLIC_A4.pdf
```

`Finalize_Public_Paper_InDesign.jsx`는 준비된 IDML을 InDesign에서 열어 16쪽·794개 독립 Story·서체·넘친 글자·프리플라이트를 검사하고 INDD와 별도 PDF를 저장합니다. `Verify_Saved_Public_Paper_InDesign.jsx`는 저장한 INDD를 디스크에서 다시 열어 검사합니다. 두 스크립트는 Python 재분석 과정에서 자동 실행되지 않으며 기존 산출물을 덮어쓰지 않습니다. `paper/` 폴더에서 파일을 찾거나 `SAJU_PAPER_OUTPUT` 환경 변수로 위치를 지정할 수 있습니다. IDML은 각 텍스트 줄을 독립 편집하는 배치형 문서이며 본문 전체가 하나로 자동 재흐름되는 문서는 아닙니다. 이 배포본의 네이티브 InDesign 검증은 완료했으며 `qa/native-validation.json`에 기록했습니다.

## 라이선스와 출처

자체 작성한 원고·코드·문서는 [Apache License 2.0](LICENSE)으로 공개합니다. [NOTICE](NOTICE)는 외부 자료의 출처와 미배포 항목을 구분합니다. 모델 가중치, 감사한 역법 엔진과 DB, 상용 서체 프로그램, 한국천문연구원 역서 PDF 전체와 제3자의 논문은 배포하지 않으며 이 라이선스로 재허락하지 않습니다. 공식 라이선스 원문은 [Apache Software Foundation](https://www.apache.org/licenses/LICENSE-2.0.txt)에서 받았습니다.

모든 출생 입력은 합성 자료이며 이용자의 출생 기록·로그를 수집하지 않았습니다. 저자는 연구 대상 소프트웨어의 개발·관리자입니다. 원고 구성·코드 작성·교차 점검에 생성형 AI 보조 도구를 사용했으며 분석과 해석의 책임은 저자에게 있습니다. 참고문헌과 공개 자료의 정확한 범위는 전체 원고를 확인해 주세요.

인용 예시: 박성모. (2026). *계산과 설명 사이의 사실 보존: 로컬 사주 언어모델의 경계 사례 평가*. 연구 원고 및 재분석 자료. https://github.com/mobidicSaju/saju-llm-fact-check
