import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)


class BackendClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
        self.timeout: float = 30.0
        logger.info(f"BackendClient initialized with base URL: {self.base_url}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Универсальный метод для запросов.
        Просто передать метод и эндпойнт и все
        """

        url = f"{self.base_url}{endpoint}"

        # Добавляем заголовки если их нет
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers

        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)

                logger.debug(f"Request to {url}: {response.status_code}")

                if response.status_code == 401:
                    logger.error(f"Authentication failed for {url}")
                    raise PermissionError("Ошибка авторизации на backend")

                response.raise_for_status()
                return response.json()                
        except httpx.TimeoutException:
            logger.error(f"Timeout for {url}")
            raise RuntimeError("Таймаут при подключении к серверу")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} \
                for {url}: {e.response.text}"
            )
            raise RuntimeError(f"Ошибка сервера: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            raise RuntimeError(f"Ошибка соединения: {str(e)}")

    # --- Пользовательские методы ---

    async def get_profile(self, telegram_id: int) -> Dict[str, Any]:
        return await self._make_request(
            method="GET",
            endpoint=f"/users/profile?telegram_id={telegram_id}"
        )

    async def get_balance(self, telegram_id: int) -> Dict[str, Any]:
        return await self._make_request(
            method="GET",
            endpoint=f"/finance/balance?telegram_id={telegram_id}"
        )

    async def get_finance_history(self, telegram_id: int) -> Dict[str, Any]:
        return await self._make_request(
            method="GET",
            endpoint=f"/finance/history?telegram_id={telegram_id}"
        )

    async def get_bot_rules(self) -> Dict[str, str]:
        return await self._make_request(
            method="GET",
            endpoint="/admin/rules/bot"
        )

    async def get_school_rules(self) -> Dict[str, str]:
        return await self._make_request(
            method="GET",
            endpoint="/admin/rules/school"
        )

    async def send_to_director(self, telegram_id: int, message: str) -> bool:
        data = await self._make_request(
            method="POST",
            endpoint="/messages/director",
            json={
                "telegram_id": telegram_id,
                "message": message,
                "user_name": "unknown"  # можно добавить из контекста
            }
        )
        return data.get("success", False)

    async def close(self) -> None:
        """
        Закрыть соединение (заглушка для совместимости)
        """
        pass
