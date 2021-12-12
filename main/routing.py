# import os

# from django.conf.urls import url
# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
# # Initialize Django ASGI application early to ensure the AppRegistry
# # is populated before importing code that may import ORM models.
# django_asgi_app = get_asgi_application()


# application = ProtocolTypeRouter({
#     # Django's ASGI application to handle traditional HTTP requests
#     "http": django_asgi_app,

#     # WebSocket chat handler
#     "websocket":
#         URLRouter([
#             url(r"^chat/admin/$", AdminChatConsumer.as_asgi()),
#             url(r"^chat/$", PublicChatConsumer.as_asgi()),]
        
#     ),
# })
from channels.routing import ProtocolTypeRouter , URLRouter
from django.core.asgi import get_asgi_application
import trading_view.routing


# application = ProtocolTypeRouter({
#     # Empty for now (http->django views is added by default)
#     'websocket': 
#         URLRouter(
#             chatapp.routing.websocket_urlpatterns
#     ),
# })

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": URLRouter(
            trading_view.routing.websocket_urlpatterns
    ),
})