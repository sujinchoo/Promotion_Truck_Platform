import json
import logging
from dataclasses import dataclass
from typing import Optional
from urllib import error, request


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str
    enabled: bool


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str], chat_id: Optional[str], enabled: bool = True):
        self.config = TelegramConfig(
            bot_token=(bot_token or "").strip(),
            chat_id=(chat_id or "").strip(),
            enabled=enabled,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.config.enabled and self.config.bot_token and self.config.chat_id)

    def send_new_lead_notification(self, lead) -> bool:
        if not self.is_configured:
            logger.info("Telegram notifier skipped because configuration is incomplete.")
            return False

        payload = {
            "chat_id": self.config.chat_id,
            "text": self._build_message(lead),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        endpoint = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=5) as response:
                return 200 <= response.status < 300
        except error.URLError:
            logger.exception("Failed to send Telegram notification for lead id=%s", getattr(lead, "id", None))
            return False

    def _build_message(self, lead) -> str:
        safe_message = (lead.message or "-").replace("<", "&lt;").replace(">", "&gt;")
        return "\n".join(
            [
                "<b>새 상담 신청이 등록되었습니다.</b>",
                f"• 이름: {lead.name}",
                f"• 연락처: {lead.phone}",
                f"• 지역: {lead.region}",
                f"• 업종/용도: {lead.business_type}",
                f"• 관심 차종: {lead.vehicle_type}",
                f"• 랜딩 페이지: {lead.landing_page}",
                f"• 연락 가능 시간: {lead.contact_time or '-'}",
                f"• 예산: {lead.budget or '-'}",
                f"• 요청사항: {safe_message}",
            ]
        )
