import motor.motor_asyncio as m_m_a
import os


class SingletonClient:
    client = None
    db = None

    @staticmethod
    def get_client():
        if SingletonClient.client is None:

            SingletonClient.client = m_m_a.AsyncIOMotorClient(
                os.environ.get("DB_URL", "")
            )

        return SingletonClient.client

    @staticmethod
    def get_data_base():
        if SingletonClient.db is None:
            client = SingletonClient.get_client()
            SingletonClient.db = client["serverManager"]

        return SingletonClient.db
