"""
key_manager.py
Điều phối và chia tải 4 API Key theo cơ chế Round-Robin (25% mỗi key) & Failover Pipeline đa tầng:
1. Round-Robin: Phân phối tuần tự từng request mới Key_1 -> Key_2 -> Key_3 -> Key_4.
2. Key Failover: Tự động xoay sang key kế tiếp khi gặp HTTP 429 hoặc Quota Exceeded.
3. Model Fallback: Hạ cấp sang model dự phòng (Gemini 2.5 Flash) khi chạm trần.
"""

import os
import asyncio
import logging
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class KeyManager:
    """
    Quản lý vòng quay Round-Robin và điều phối Failover cho 4 API Key của Google Gemini.
    """
    def __init__(self, api_keys: List[str] = None):
        if not api_keys:
            env_keys = os.getenv("GEMINI_API_KEYS", "")
            if env_keys:
                self.api_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
            else:
                single = os.getenv("GEMINI_API_KEY", "")
                self.api_keys = [single.strip()] if single else []
        else:
            self.api_keys = [k.strip() for k in api_keys if k and k.strip()]

        if not self.api_keys:
            raise ValueError("Không tìm thấy GEMINI_API_KEYS hoặc GEMINI_API_KEY trong file .env.")

        self._index = 0
        self._lock = asyncio.Lock()
        logger.info(f"[KeyManager] Initialized with {len(self.api_keys)} API keys (Round-Robin enabled).")

    @property
    def total_keys(self) -> int:
        return len(self.api_keys)

    def get_all_keys(self) -> List[str]:
        return list(self.api_keys)

    async def get_next_key(self) -> Tuple[str, int]:
        """
        Lấy key kế tiếp theo thứ tự vòng quay Round-Robin (chia đều tải 25% cho mỗi key).
        Trả về tuple: (api_key, key_number: 1..N)
        """
        async with self._lock:
            idx = self._index % len(self.api_keys)
            self._index = (self._index + 1) % len(self.api_keys)
            key_num = idx + 1
            key_val = self.api_keys[idx]
            logger.info(f"[KeyManager Round-Robin] Request dispatched to Key {key_num} (...{key_val[-6:]})")
            return key_val, key_num

    def get_failover_chain(self, current_key_num: int) -> List[Tuple[str, int]]:
        """
        Tạo danh sách các key dự phòng tiếp theo theo vòng tròn nếu key hiện tại gặp lỗi 429.
        Ví dụ: nếu Key 2 lỗi -> trả về [Key 3, Key 4, Key 1].
        """
        start_idx = current_key_num % len(self.api_keys)
        chain = []
        for i in range(len(self.api_keys) - 1):
            idx = (start_idx + i) % len(self.api_keys)
            chain.append((self.api_keys[idx], idx + 1))
        return chain

# Singleton instance
_global_key_manager = None

def get_key_manager() -> KeyManager:
    global _global_key_manager
    if _global_key_manager is None:
        _global_key_manager = KeyManager()
    return _global_key_manager
