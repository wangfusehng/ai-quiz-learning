class BizError(Exception):
    def __init__(self, status_code: int, error: str) -> None:
        self.status_code = status_code
        self.error = error
        super().__init__(error)


class EmptyModelError(Exception):
    """模型返回空 content 或无法解析。"""


class UpstreamError(Exception):
    """DeepSeek / 网络等上游失败。"""
