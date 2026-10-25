import ipaddress

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator
from yookassa import Configuration

load_dotenv()

class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr
    remnawave_token: SecretStr
    remnawave_url: str
    remnawave_internal_squad: str
    base_webhook_url: str
    wg_easy_password: SecretStr
    wg_easy_url: str
    yookassa_account_id: str
    yookassa_secret_key: SecretStr
    yookassa_networks: str | list[ipaddress.IPv4Network | ipaddress.IPv6Network]

    # Добавьте недостающие поля для базы данных:
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str

    model_config = SettingsConfigDict(env_file=".env")

    base_webhook_url: str

    @field_validator("yookassa_networks", mode="before")
    @classmethod
    def _parse_networks(cls, value: any) -> list:

        if isinstance(value, str):
            return [
                ipaddress.ip_network(net.strip())
                for net in value.split(",")
                if net.strip()
            ]
        return value


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()

Configuration.configure(
    account_id=config.yookassa_account_id,
    secret_key=config.yookassa_secret_key.get_secret_value()
)