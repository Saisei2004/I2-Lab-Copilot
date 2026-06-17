"""i2_core: 設定・ロギング・GCP クライアントの共通基盤。"""

from i2_core.config import Settings, settings
from i2_core.logging import get_logger

__all__ = ["Settings", "get_logger", "settings"]
