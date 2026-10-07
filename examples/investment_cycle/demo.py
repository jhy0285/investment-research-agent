"""Generate the authored synthetic approval and follow-up example offline.

Run from the repository root: python -m examples.investment_cycle.demo --output ...
Shares the hand-checkable test fixture; never downloads or invents market data.
"""
import argparse
from pathlib import Path

from investment_research.decision_data import save
from investment_research.decision_journal import record, review, persist_review
from investment_research.decision_report import render_decision, render_review
from investment_research.investment_cycle import evaluate
from tests.test_investment_cycle import experiment, outcome_prices


def main():
    parser=argparse.ArgumentParser(description='합성 투자 판단과 사후 손실 평가의 오프라인 예제')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('새 출력 디렉터리를 지정하세요')
    plan,snapshot=experiment()
    result=evaluate(plan,snapshot)
    save(args.output/'plan.json',plan)
    save(args.output/'research_snapshot.json',snapshot)
    save(args.output/'decision.json',result)
    (args.output/'report.md').write_text(render_decision(result),encoding='utf-8')
    record(args.output/'journal',result)
    prices=outcome_prices(plan['candidates'][0])
    save(args.output/'outcome_prices.json',prices)
    pending=review(args.output/'journal',prices,snapshot['as_of'])
    save(args.output/'pending_review.json',pending)
    # Future dates belong only to this authored experiment, never market claims.
    completed=review(args.output/'journal',prices,'2026-12-10T00:00:00+00:00')
    save(args.output/'outcome_review.json',completed)
    persist_review(args.output/'journal',completed)
    (args.output/'outcome_report.md').write_text(render_review(completed),encoding='utf-8')
    print('합성 검증 보고서:',args.output/'report.md')
    print('합성 사후검증:',args.output/'outcome_report.md')


if __name__=='__main__':main()
