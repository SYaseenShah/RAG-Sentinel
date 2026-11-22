"""Run the labelled synthetic benchmark from the project root."""
import json
from evaluation.metrics import evaluate_benchmark

if __name__ == "__main__":
    result = evaluate_benchmark()
    print(json.dumps({k: v for k, v in result.items() if k not in {"details", "report"}}, indent=2))
    print("\nPer-sample decisions:")
    for item in result["details"]:
        print(f"{item['sample_id']} | actual={item['actual']} | predicted={item['predicted']} | risk={item['risk_score']} | {item['decision']}")
