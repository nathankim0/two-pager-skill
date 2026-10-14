![Two Pager — Codex와 Claude를 위한 2페이지 의사결정 문서](docs/cover.png)

# Two Pager Skill

긴 메모를 **두 페이지의 대표 보고·제안서**로 압축하는 Codex / Claude Code 공용 스킬입니다. 한글 글자 잘림, 불필요한 숫자 강조, 이미지 배치, 매번 반복하던 PDF 출력 과정을 줄이기 위해 만들었습니다.

**결과물:** 편집 가능한 HTML, 공유용 PDF, 페이지별 검토 이미지.

## 예제: 동네 도서관 예약·알림 서비스 개선

실제 기관과 무관한 가상 사례입니다. 문의량·기준선·목표도 모두 예제용이며, 특정 회사의 자료·로고·UI를 포함하지 않습니다. 아래 이미지는 AI가 상상한 문서가 아니라 **이 스킬의 HTML을 브라우저에서 실제 출력한 결과**입니다.

### 1페이지 · 현황, 서비스 설계, 운영 대안

![도서관 예제 1페이지](docs/example-page-1.png)

### 2페이지 · 기대 효과, 검증 지표, 로드맵

![도서관 예제 2페이지](docs/example-page-2.png)

[예제 PDF](docs/library-two-pager.pdf) · [예제 HTML](docs/library-two-pager.html)

## 설치

같은 `skills/two-pager/SKILL.md`를 두 도구가 읽습니다. 특정 모델 API, MCP 서버, 다른 스킬이 필요하지 않습니다. 로컬 파일 생성과 명령 실행이 가능한 Codex 또는 Claude Code 환경을 사용하세요.

### macOS / Linux

```bash
git clone https://github.com/nathankim0/two-pager-skill.git
cd two-pager-skill
```

Codex에 설치:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/two-pager" ~/.agents/skills/two-pager
```

Claude Code에 설치:

```bash
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/two-pager" ~/.claude/skills/two-pager
```

두 명령을 모두 실행하면 같은 스킬을 함께 사용합니다. 이미 같은 이름의 스킬이 있다면 덮어쓰지 말고 위치를 먼저 확인하세요. 링크가 가리키는 저장소를 옮기거나 삭제하면 스킬을 사용할 수 없습니다. 업데이트는 이 저장소에서 `git pull`로 반영합니다.

프로젝트에서만 사용하려면 사용자 홈 대신 프로젝트의 `.agents/skills/` 또는 `.claude/skills/`에 링크하거나 폴더를 복사하세요.

### Windows PowerShell

심볼릭 링크 권한 없이 복사해 설치할 수 있습니다.

```powershell
git clone https://github.com/nathankim0/two-pager-skill.git
cd two-pager-skill

New-Item -ItemType Directory -Force "$HOME/.agents/skills"
New-Item -ItemType Directory -Force "$HOME/.claude/skills"
Copy-Item -Recurse ./skills/two-pager "$HOME/.agents/skills/two-pager"
Copy-Item -Recurse ./skills/two-pager "$HOME/.claude/skills/two-pager"
```

대상 폴더가 없는 상태에서 실행하세요. 복사 설치는 저장소를 업데이트한 뒤 설치 폴더에도 변경 파일을 반영해야 합니다.

Codex에서 스킬이 보이지 않으면 새 세션을 시작하세요. Claude Code는 `/two-pager`로 확인할 수 있습니다. 설치 경로는 [Codex 공식 문서](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills), [Claude Code 공식 문서](https://code.claude.com/docs/en/skills#choose-where-skills-load)를 따릅니다.

## 사용

Codex:

```text
$two-pager
아래 메모를 대표 보고용 한글 2pager로 만들어.
첨부한 장표의 배치와 밀도를 참고하고, 중요한 근거와 조건은 남겨줘.
```

Claude Code:

```text
/two-pager
이 제안서를 두 페이지로 압축하고 HTML과 PDF를 만들어줘.
1페이지는 현황과 제안, 2페이지는 효과와 추진 계획으로 구성해줘.
```

참고 장표, 사용자 이미지, 회사 글꼴·로고가 있으면 함께 제공하면 됩니다. 사용자가 제공한 AI UI는 시안으로 표시하고, 문서와 모순되는 보상·가격·동작은 그대로 옮기지 않습니다.

## 직접 실행

Python **3.10 이상**이 필요합니다. 첫 렌더에서 Playwright·pypdf·Pillow를 공용 캐시에 설치합니다. 이후에는 같은 런타임을 재사용합니다. 설치된 Chrome/Chromium을 먼저 사용하고, 없으면 Chromium을 한 번 다운로드합니다.

Python 런타임은 `~/.cache/two-pager/`에 보관하며 `XDG_CACHE_HOME` 설정을 따릅니다. 로컬 macOS·설치된 Chrome에서 의존성 설치를 제외한 2페이지 PDF·미리보기·검사 재실행은 약 2.4초였습니다. 실행 시간은 환경과 문서에 따라 달라집니다.

```bash
# 1. 편집할 초안 생성
python3 skills/two-pager/scripts/two_pager.py scaffold ./work/brief \
  --title "동네 도서관 예약·알림 서비스 개선" --brand "LIBRARY"

# 2. work/brief/two-pager.html의 예제 내용을 실제 제안으로 수정

# 3. 한 번에 출력·검사·미리보기 생성
python3 skills/two-pager/scripts/two_pager.py render \
  ./work/brief/two-pager.html --output-dir ./output/brief
```

생성 파일:

```text
output/brief/
├── two-pager.html
├── two-pager.pdf
└── .qa/two-pager/
    ├── page-1.png
    ├── page-2.png
    └── report.json
```

`.qa`의 두 이미지를 확인한 뒤 HTML·PDF만 전달합니다. 레이아웃 검사가 실패하면 미리보기와 보고서는 남기고, 이전에 성공한 최종 파일은 보존합니다.

이미지 자르기:

```bash
python3 skills/two-pager/scripts/two_pager.py crop ./ui.png \
  --box 344 112 312 600 --output ./work/brief/quest.png
```

`--box`는 원본 좌표의 `x y 너비 높이`입니다. 예제 좌표를 다른 이미지에 그대로 쓰지 마세요. HTML에 `<img src="quest.png" alt="AI 생성 퀘스트 UI 시안">`처럼 넣으면 렌더할 때 파일 내부에 포함됩니다. 원본은 변경하지 않습니다. 상대 경로 이미지와 인라인 CSS를 권장하며, 원격 리소스는 출력 중 차단합니다.

브라우저를 지정하려면 `render --browser /path/to/chrome`을 사용하세요. Linux에서 한글이 네모로 나오면 한국어 글꼴을 설치하세요. 예를 들어 Ubuntu에서는 `fonts-noto-cjk`를 사용할 수 있습니다. 서버에 Chromium 시스템 라이브러리가 없다면 Playwright 런타임에서 `python -m playwright install --with-deps chromium`이 필요할 수 있습니다.

## 실제 시행착오를 줄이는 방법

| 오래 걸렸던 부분 | 이 스킬의 처리 |
| --- | --- |
| 숫자가 크다는 이유로 핵심보다 먼저 보임 | 강조는 의사결정 중요도로 정하고 근거 수치는 본문에 배치 |
| 한글이 음절 단위로 줄바꿈됨 | `word-break: keep-all`과 의미 단위 개행 |
| 단계 라벨이 늘어나 마지막 행이 밀림 | 짧은 두 줄 라벨과 고정된 콘텐츠 영역 |
| 그림을 뒤늦게 넣어 전체 재배치 | 이미지 공간을 먼저 확보하고 필요한 부분만 자르기 |
| 가상 UI와 제안 조건이 충돌 | AI 시안 표시와 내용에 맞는 영역 선택 |
| 매번 가상환경과 패키지 설치 | Python 버전·의존성 목록 기준의 지속 캐시 |
| PDF·이미지·페이지 수 검사를 각각 실행 | 한 번의 브라우저 실행으로 묶음 처리 |
| 실패한 수정이 정상 PDF를 덮어씀 | 검사 성공 후에만 최종 파일 교체 |

세부 원칙은 [레이아웃 노트](skills/two-pager/references/layout-lessons.md)에 있습니다. 기계 검사는 텍스트·이미지 겹침, 영역 초과, PDF 페이지 수·크기를 확인합니다. 내용의 사실성, 색 대비, 글꼴 품질, 모든 앱에서의 표시를 자동으로 보증하지 않습니다.

## 개발·검증

```bash
python3 -m pip install -r skills/two-pager/scripts/requirements.txt
python3 -m unittest discover -s tests -v
```

테스트는 두 페이지 출력과 한글 추출, 범위를 벗어난 자르기 거부, 원본 이미지 보존, 외부 이미지 거부, 겹침·페이지 수 실패 시 기존 최종 파일 보존을 확인합니다. GitHub Actions에서는 Linux Chromium과 한국어 글꼴로 같은 테스트를 실행합니다.

## 범위

기본 템플릿은 16:9 가로형 두 페이지입니다. 사용자의 레퍼런스가 다르면 HTML과 인쇄 크기를 함께 바꿀 수 있습니다. 긴 슬라이드 덱이나 편집 가능한 PPTX 생성은 이 도구의 범위에 포함하지 않습니다.

대문은 AI로 생성한 소개 이미지이며, 생성 프롬프트는 [docs/cover-prompt.txt](docs/cover-prompt.txt)에 있습니다. 두 도서관 예제 이미지는 실제 렌더 결과입니다. 라이선스는 [MIT](LICENSE)입니다.
