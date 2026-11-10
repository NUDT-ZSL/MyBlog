from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/<str:slug>/", views.post_detail, name="post_detail"),
    path("categories/<str:slug>/", views.category_detail, name="category_detail"),
    path("tags/<str:slug>/", views.tag_detail, name="tag_detail"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<str:slug>/", views.project_detail, name="project_detail"),
    path("notes/", views.note_list, name="note_list"),
    path("notes/<str:slug>/", views.note_detail, name="note_detail"),
    path("archive/", views.archive, name="archive"),
    path("search/", views.search, name="search"),
    path("api/search/", views.search_api, name="search_api"),
    path("about/", views.about, name="about"),
    path("friends/", views.friends, name="friends"),
    path("books/", views.books, name="books"),
    path("tools/", views.tools, name="tools"),
    path("resume/", views.resume, name="resume"),
    path("feed/", LatestPostsFeed(), name="rss_feed"),
]
