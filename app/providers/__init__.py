from app.models.channel import ChannelProvider
from app.providers import slack
from app.providers.base import ProviderFn

REGISTRY: dict[ChannelProvider, ProviderFn] = {
    ChannelProvider.slack: slack.send,
}
