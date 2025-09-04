import yaml
from pydantic import \
    BaseModel, PositiveInt, ValidationError, HttpUrl, Field


class System(BaseModel):

    time_zone: str


class Bot(BaseModel):

    id: PositiveInt
    name: str
    link: HttpUrl
    token: str


class MessageEffect(BaseModel):

    fire: str
    thumb_up: str
    thumb_down: str
    heart: str
    greeting: str
    poo: str


class Admins(BaseModel):
    ids: list[PositiveInt]


class Superadmins(BaseModel):
    ids: list[PositiveInt]


class Redis(BaseModel):

    host: str
    fsm: str
    users: str
    temp: str


class Google(BaseModel):

    onboarding_id: str
    vitrina_tab: str
    intern_tab: str
    service_account_json: str


class OpenAI(BaseModel):

    api_key: str
    model: str
    provider: str
    embedding_model: str


class SystemPrompt(BaseModel):

    prompt: str


class Config(BaseModel):

    system: System
    bot: Bot
    bot_test: Bot
    message_effect: MessageEffect
    admins: Admins
    superadmins: Superadmins
    redis: Redis
    openai: OpenAI
    system_prompt: SystemPrompt
    google: Google

# Load the YAML configuration file
def load_config() -> Config:
    import os

    with open('config.yaml', 'r') as file:
        config_data = yaml.safe_load(file)

    # Get bot configuration from environment variable
    bot_config = os.getenv('BOT_CONFIG', 'bot')
    
    # Select the appropriate bot configuration
    if bot_config == 'bot_test':
        # Use bot_test configuration for development
        config_data['bot'] = config_data['bot_test']
        print(f"Using development bot configuration: {config_data['bot_test']['name']}")
    else:
        # Use bot configuration for production
        print(f"Using production bot configuration: {config_data['bot']['name']}")

    try:
        config: Config = Config(**config_data)
    except ValidationError as e:
        print("Config validation error:", e.json(indent=4))

    return config
    
    
def main():
    config: Config = load_config()
    print(config.model_dump_json(indent=4))


if __name__ == "__main__":
    main()