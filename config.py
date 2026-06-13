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

    wg_easy_password: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    base_webhook_url: str

    yookassa_account_id: str
    yookassa_secret_key: SecretStr

    yookassa_networks: str | list[ipaddress.IPv4Network | ipaddress.IPv6Network]

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