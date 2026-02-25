from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Run, Example
import os
from app import app

client = Client()

# 准备评测数据集（可手动创建或从 huggingface 导入）
dataset_name = "multi-agent-math-search-qa"

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name)
    examples = [
        {
            "inputs": {"question": "2024年诺贝尔物理学奖得主是谁？"},
            "outputs": {"answer": "John Hopfield 和 Geoffrey Hinton"}  # 简化，实际应更精确
        },
        {
            "inputs": {"question": "求解方程 x^3 - 6x^2 + 11x - 6 = 0 的整数根"},
            "outputs": {"answer": "1,2,3"}
        },
        # ... 再加 8~20 条
    ]
    client.create_examples(
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
        dataset_id=dataset.id
    )

# 评测函数
def agent_predict(inputs: dict):
    config = {"configurable": {"thread_id": "eval_" + str(hash(inputs["question"]))}}
    events = list(app.stream({"messages": [("human", inputs["question"])]}, config))
    final_msg = events[-1]["messages"][-1].content
    return {"answer": final_msg}

def match_answer(run: Run, example: Example) -> dict:
    prediction = run.outputs.get("answer", "").strip().lower()
    ground_truth = example.outputs.get("answer", "").strip().lower()
    score = 1.0 if ground_truth in prediction or prediction in ground_truth else 0.0
    return {"key": "correct", "score": score}

# 执行离线评测
results = evaluate(
    agent_predict,
    data=dataset_name,
    evaluators=[match_answer],
    experiment_prefix="supervisor-gpt4o-deepseek-v1",
    client=client,
    max_concurrency=3,
)

print(results)