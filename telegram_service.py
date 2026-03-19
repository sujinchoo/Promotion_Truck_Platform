import logging
from dataclasses import dataclass
from datetime import timezone
from typing import Optional
from zoneinfo import ZoneInfo

import requests


logger = logging.getLogger(__name__)
KOREA_TIMEZONE = ZoneInfo("Asia/Seoul")


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

        try:
            response = requests.post(endpoint, json=payload, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            logger.exception("Failed to send Telegram message for lead id=%s", getattr(lead, "id", None))
            return False

    def _build_message(self, lead) -> str:
        safe_message = (lead.message or "-").replace("<", "&lt;").replace(">", "&gt;")
        created_at = getattr(lead, "created_at", None)
        formatted_created_at = self._format_created_at(created_at)
        return "\n".join(
            [
                "🚚 <b>신규 화물차 상담 접수</b>",
                "",
                f"👤 이름: {lead.name}",
                f"📞 연락처: {lead.phone}",
                f"📍 지역: {lead.region}",
                f"🏢 업종/용도: {lead.business_type}",
                f"🚛 관심차종: {lead.vehicle_type}",
                f"💰 예산: {lead.budget or '-'}",
                f"🕒 연락 가능 시간: {lead.contact_time or '-'}",
                f"🌐 랜딩 페이지: {lead.landing_page}",
                f"📝 요청사항: {safe_message}",
                "",
                f"⏰ 접수 시간: {formatted_created_at}",
            ]
        )
    def _format_created_at(self, created_at) -> str:
        if not created_at:
            return "-"

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return created_at.astimezone(KOREA_TIMEZONE).strftime("%Y-%m-%d %H:%M")

