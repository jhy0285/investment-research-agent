#!/usr/bin/env bash
# 한 번의 섀도 점검: 이력 수집 -> 조사 -> 섀도 판단 두 건 -> 사후 평가. 사람의 review는 쓰지 않는다(금액 0 기록만 만든다).
# 사용: JOURNAL=<일지 디렉터리> RUNS=<실행 폴더> bash examples/strategy_library/weekly_shadow.sh
# 실제 시세가 들어가므로 JOURNAL과 RUNS는 공개 저장소에 두지 않는다.
set -euo pipefail
JOURNAL="${JOURNAL:-reports/investment_journal}"
RUNS="${RUNS:-reports/shadow_runs}"
DAY="$(date -u +%Y-%m-%dT%H%M%SZ)"
DIR="$RUNS/$DAY"
PY="python -m investment_research"
mkdir -p "$DIR"

# 1. 이력 (HISTORY를 주면 이미 받은 이력을 쓴다)
HISTORY="${HISTORY:-$DIR/history}"
if [ ! -d "$HISTORY" ]; then
  $PY invest history acquire examples/investment_history/crypto_trend_library_spec.json --output "$HISTORY" > "$DIR/history.out"
fi
$PY invest history replay "$HISTORY" > /dev/null

# 2. 조사 (판단 시각에 7일 넘게 오래되면 판단이 보류된다)
RESEARCH="${RESEARCH:-$DIR/ask}"
if [ ! -d "$RESEARCH" ]; then
  $PY ask '현재 신규 자금을 투자한다면 어디에 투자하는 것이 가장 합리적인가?' --run-dir "$RESEARCH" > "$DIR/ask.out"
fi

# 3. 섀도 판단 (등록된 전략만 기록된다. 먼저 invest strategy register를 한 번 실행해 둔다)
for kind in trend momentum; do
  $PY invest run "examples/strategy_library/shadow_plan_$kind.json" --research-run "$RESEARCH" --history "$HISTORY" \
    --run-dir "$DIR/decision_$kind" --journal "$JOURNAL" > "$DIR/decision_$kind.out"
done

# 4. 지난 섀도 판단의 사후 평가 (성숙한 결과가 없으면 비어 있다)
$PY invest review --journal "$JOURNAL" --history "$HISTORY" --as-of "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)" \
  --run-dir "$DIR/review" > "$DIR/review.out"
echo "완료: $DIR"
