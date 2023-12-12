from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    GenreViewSet,
    ActorViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("cinema_halls", TheatreHallViewSet)
router.register("movies", PlayViewSet)
router.register("movie_sessions", PerformanceViewSet)
router.register("orders", ReservationViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "theatre"
