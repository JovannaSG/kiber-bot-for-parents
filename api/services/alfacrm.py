import httpx
import logging
from typing import Dict, Any, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class AlfaCRMClient:
    def __init__(self) -> None:
        self.base_url: str = "https://{}/v2api/{}/".format(
            settings.alfacrm_hostname,
            settings.alfacrm_branch_id
        )
        self.api_key: str = settings.alfacrm_api_key.get_secret_value()
        self.branch_id = settings.alfacrm_branch_id
        self.headers = {
            "X-ALFACRM-TOKEN": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.timeout = 30.0
        logger.info(f"AlfaCRM client initialized for branch {self.branch_id}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Универсальный метод для запросов к AlfaCRM
        """

        # Create URL
        url: str = self.base_url + endpoint
        
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers

        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Making {method} request to {url}")
                response = await client.request(method, url, **kwargs)

                if response.status_code == 401:
                    logger.error("AlfaCRM authentication failed")
                    raise PermissionError("Invalid AlfaCRM API token")

                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout for AlfaCRM request: {url}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"AlfaCRM API error {e.response.status_code}: \
                {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AlfaCRM request: {e}")
            raise

    # --- Customer methods ---

    async def get_customer_by_telegram_id(
        self,
        telegram_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Найти клиента по telegram_id в custom полях
        """

        try:
            # Ищем клиента в AlfaCRM по кастомному полю telegram_id
            params: Dict[str, Any] = {
                "page": 0,
                "with": [
                    "customers",
                    "customers.custom_fields",
                    "customers.balance"
                ]
            }
            
            response: Dict[str, Any] = await self._make_request(
                method="GET",
                endpoint="/customer/index",
                params=params
            )

            customers: List[Dict] = response.get("items", [])
            for customer in customers:
                custom_fields: Dict = customer.get("custom_fields", {})
                # Ищем поле с telegram_id (может быть field_1, field_2 и т.д.)
                for field_key, field_value in custom_fields.items():
                    if (
                        isinstance(field_value, str) and
                        field_value.strip() == str(telegram_id)
                    ):
                        return customer
                    if (
                        isinstance(field_value, int) and
                        field_value == telegram_id
                    ):
                        return customer

            # Если не нашли по telegram_id, можно попробовать по другим полям
            # Например, по ID в CRM
            return None
        except Exception as e:
            logger.error(
                f"Error finding customer by telegram_id {telegram_id}: {e}"
            )
            return None

    async def get_customer_by_phone(
        self,
        phone: str
    ) -> Optional[Dict[str, Any]]:
        """
        Найти клиента по номеру телефона
        """

        try:
            params: Dict[str, Any] = {
                "page": 0,
                "phone": phone,
                "with": [
                    "customers",
                    "customers.custom_fields",
                    "customers.balance"
                ]
            }
            
            response: Dict[str, Any] = await self._make_request(
                method="GET",
                endpoint="/customer/index",
                params=params
            )
            customers: List[Dict] = response.get("items", [])
            
            if customers:
                return customers[0]
            return None
        except Exception as e:
            logger.error(f"Error finding customer by phone {phone}: {e}")
            return None

    async def get_customer_balance(self, customer_id: int) -> Dict[str, Any]:
        """
        Получить баланс клиента
        """

        try:
            params: Dict[str, Any] = {
                "id": customer_id,
                "with": ["balance"]
            }

            response: Dict[str, Any] = await self._make_request(
                method="GET",
                endpoint="/customer/index",
                params=params
            )
            customers: List[Dict] = response.get("items", [])

            if not customers:
                return {"balance": 0, "paid_lessons": 0}

            customer: Dict[str, Any] = customers[0]
            balance_data: Dict[str, Any] = customer.get("balance", {})

            # Преобразуем данные AlfaCRM в наш формат
            return {
                "balance": float(balance_data.get("balance", 0)),
                "paid_lessons": int(balance_data.get("lesson_balance", 0)),
                "bonus_points": int(balance_data.get("bonus_balance", 0))
            }
        except Exception as e:
            logger.error(
                f"Error getting balance for customer {customer_id}: {e}"
            )
            return {"balance": 0, "paid_lessons": 0, "bonus_points": 0}

    async def get_customer_transactions(
        self, 
        customer_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]] | List:
        """
        Получить историю транзакций клиента
        """

        try:
            params: Dict[str, Any] = {
                "page": 0,
                "customer_id": customer_id,
                "with": ["transactions"],
                "limit": limit,
                "order": "date_desc"
            }

            response: Dict[str, Any] = await self._make_request(
                method="GET",
                endpoint="/transaction/index",
                params=params
            )
            transactions: List[Dict] = response.get("items", [])

            # Преобразуем в наш формат
            formatted_transactions: List[Dict[str, Any]] = []
            for tx in transactions[:limit]:
                formatted_transactions.append({
                    "type": "income" if tx.get("type") in ["payment", "correction_in"] else "expense",
                    "amount": abs(float(tx.get("value", 0))),
                    "currency": tx.get("currency", "руб."),
                    "description": tx.get("comment", ""),
                    "date": tx.get("date", "")
                })

            return formatted_transactions
        except Exception as e:
            logger.error(
                f"Error getting transactions for customer {customer_id}: {e}"
            )
            return []

    async def get_customer_groups(self, customer_id: int) -> List[str]:
        """
        Получить группы клиента
        """

        try:
            params = {
                "id": customer_id,
                "with": ["groups"]
            }
            
            response = await self._make_request("GET", "/customer/index", params=params)
            customers = response.get("items", [])
            
            if not customers:
                return []
            
            customer = customers[0]
            groups = customer.get("groups", [])
            
            return [group.get("name", "") for group in groups if group.get("name")]
            
        except Exception as e:
            logger.error(f"Error getting groups for customer {customer_id}: {e}")
            return []

    async def search_customers(self, query: str) -> List[Dict[str, Any]]:
        """Поиск клиентов по различным параметрам"""
        try:
            params = {
                "page": 0,
                "search": query,
                "with": ["customers", "customers.custom_fields"]
            }
            
            response = await self._make_request("GET", "/customer/index", params=params)
            return response.get("items", [])
            
        except Exception as e:
            logger.error(f"Error searching customers with query {query}: {e}")
            return []

    async def update_customer_telegram_id(
        self, 
        customer_id: int, 
        telegram_id: int,
        field_name: str = "telegram_id"
    ) -> bool:
        """Обновить telegram_id в кастомном поле клиента"""
        try:
            # Получаем текущие данные клиента
            params = {"id": customer_id}
            response = await self._make_request("GET", "/customer/index", params=params)
            customers = response.get("items", [])
            
            if not customers:
                return False
            
            customer = customers[0]
            custom_fields = customer.get("custom_fields", {})
            
            # Обновляем поле с telegram_id
            # Нужно определить ID кастомного поля в вашем AlfaCRM
            # Например, если поле называется "telegram_id" и имеет ID 1:
            custom_fields["1"] = str(telegram_id)
            
            # Отправляем обновление
            update_data = {
                "id": customer_id,
                "custom_fields": custom_fields
            }
            
            await self._make_request("POST", "/customer/update", json=update_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating telegram_id for customer {customer_id}: {e}")
            return False


alfacrm_client = AlfaCRMClient()
