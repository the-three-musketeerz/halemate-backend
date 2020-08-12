from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import halemate.routing

application = ProtocolTypeRouter({
        'websocket': AuthMiddlewareStack(
        URLRouter(
            halemate.routing.websocket_urlpatterns
        )
    ),
})