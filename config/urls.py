"""URL configuration for IR 之下."""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from blog.sitemaps import BlogSitemap, NoteSitemap, PageSitemap, ProjectSitemap
from blog.views import robots_txt

admin.site.site_header = "IR 之下 · 内容管理"
admin.site.site_title = "IR 之下"
admin.site.index_title = "写作与站点管理"

sitemaps = {
    "posts": BlogSitemap,
    "notes": NoteSitemap,
    "projects": ProjectSitemap,
    "pages": PageSitemap,
}

handler404 = "blog.views.custom_404"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("blog.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
