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
    message_effect: MessageEffect
    admins: Admins
    superadmins: Superadmins
    redis: Redis
    openai: OpenAI
    system_prompt: SystemPrompt


# Load the YAML configuration file
def load_config() -> Config:

    with open('config.yaml', 'r') as file:
        config_data = yaml.safe_load(file)

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