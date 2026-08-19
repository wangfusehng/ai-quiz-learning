from copy import deepcopy

from app.schemas.quiz import QuizDocument

MATERIAL = (
    "卡尼曼讲过，人对确定损失的厌恶，常常大过对同等收益的喜欢。"
    "看完视频觉得懂了，转头却说不清损失厌恶到底在怕什么。"
    "真正的难点不是记术语，而是把确定亏掉和确定赚到放在同一笔钱上对比。"
    "看懂是熟悉感，能讲出来才是提取练习。"
    "测验效应说明，主动回忆比再看一遍更有助于记住关键概念。"
    "材料强调这不是鼓励冒险亏损，也不是通货膨胀的另一种说法。"
    "同样一笔钱，确定亏掉往往比确定赚到更扎心。"
    "熟悉感会让人误以为已经掌握，直到被提问才发现讲不完整。"
)

QUOTE_LOSS = "人对确定损失的厌恶，常常大过对同等收益的喜欢"
QUOTE_PRACTICE = "能讲出来才是提取练习"
QUOTE_TEST = "主动回忆比再看一遍更有助于记住关键概念"
QUOTE_MONEY = "确定亏掉往往比确定赚到更扎心"
QUOTE_FAMILIAR = "看懂是熟悉感"
QUOTE_ASK = "直到被提问才发现讲不完整"


def valid_quiz_payload() -> dict:
    def choice(qid: str, stem: str, quote: str, locator: str, point: str, correct: str = "B") -> dict:
        return {
            "id": qid,
            "type": "single_choice",
            "stem": stem,
            "options": [
                {"id": "A", "text": "人总是更爱冒险，所以会主动追求亏损。"},
                {"id": "B", "text": "同样一笔钱，确定亏掉往往比确定赚到更扎心。"},
                {"id": "C", "text": "这只是通货膨胀的另一种说法。"},
                {"id": "D", "text": "看懂视频就等于能讲清楚概念。"},
            ],
            "correctOptionId": correct,
            "explanation": "材料说的是同一笔钱的亏和赚不对称，不是鼓励你去亏。",
            "sourceQuote": {"text": quote, "locator": locator},
            "knowledgePoint": point,
        }

    return {
        "schemaVersion": "1",
        "quizId": "quiz-fixture-1",
        "source": {
            "type": "text",
            "title": "损失厌恶",
            "excerpt": MATERIAL[:80],
            "charCount": len(MATERIAL),
        },
        "meta": {
            "model": "deepseek-v4-flash",
            "thinking": False,
            "questionCount": 7,
            "estimatedMinutes": 8,
            "aiGenerated": True,
        },
        "questions": [
            choice("q1", "哪句更贴近材料？", QUOTE_LOSS, "第1段", "损失厌恶"),
            choice("q2", "看懂和会讲的差别？", QUOTE_FAMILIAR, "第2段", "熟悉感"),
            choice("q3", "提取练习指什么？", QUOTE_PRACTICE, "第3段", "提取练习"),
            choice("q4", "测验效应强调什么？", QUOTE_TEST, "第4段", "测验效应"),
            choice("q5", "同一笔钱怎么比？", QUOTE_MONEY, "第5段", "亏赚不对称"),
            choice("q6", "为什么以为自己会了？", QUOTE_ASK, "第6段", "被提问才知缺口"),
            {
                "id": "q7",
                "type": "short_answer",
                "stem": "用自己的话说明：为什么看懂了视频不等于能讲出损失厌恶？",
                "rubric": {"keyPoints": ["看懂是熟悉感", "能讲出来才是提取练习"]},
                "explanation": "熟悉感不等于提取成功。",
                "sourceQuote": {"text": QUOTE_PRACTICE, "locator": "第3段"},
                "knowledgePoint": "看懂与会讲",
            },
        ],
    }


def valid_quiz() -> QuizDocument:
    return QuizDocument.model_validate(valid_quiz_payload())


def quiz_with_fake_quote() -> QuizDocument:
    payload = deepcopy(valid_quiz_payload())
    payload["questions"][0]["sourceQuote"]["text"] = "这段话材料里根本没有出现过"
    return QuizDocument.model_validate(payload)


def valid_report_payload() -> dict:
    return {
        "schemaVersion": "1",
        "quizId": "quiz-fixture-1",
        "aiGenerated": True,
        "headline": "我刚刚搞懂了《损失厌恶》",
        "oneLiner": "损失厌恶不是爱冒险，是确定亏掉比确定赚到更扎心。",
        "pointsBitten": ["亏和赚不对称", "熟悉感不是掌握"],
        "stillFuzzy": ["和风险越大收益越大怎么分开"],
        "goldQuote": {"text": QUOTE_LOSS, "locator": "第1段"},
        "invite": "用大约 3 分钟打同一关",
        "scoreHint": {"correct": 4, "total": 6, "shortAnswerNote": "短答另计"},
    }


def sample_answers(*, wrong_first: bool = False) -> dict:
    first = "A" if wrong_first else "B"
    return {
        "quizId": "quiz-fixture-1",
        "startedAt": "2026-08-19T01:00:00Z",
        "submittedAt": "2026-08-19T01:08:00Z",
        "answers": [
            {"questionId": "q1", "type": "single_choice", "optionId": first},
            {"questionId": "q2", "type": "single_choice", "optionId": "B"},
            {"questionId": "q3", "type": "single_choice", "optionId": "B"},
            {"questionId": "q4", "type": "single_choice", "optionId": "B"},
            {"questionId": "q5", "type": "single_choice", "optionId": "B"},
            {"questionId": "q6", "type": "single_choice", "optionId": "A"},
            {"questionId": "q7", "type": "short_answer", "text": "当时听得很顺，但没有被提问。"},
        ],
    }
