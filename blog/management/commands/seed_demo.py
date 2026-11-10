from __future__ import annotations

import os
import secrets
from datetime import date, datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.demo_assets import BOOKS, FRIENDS, NOTES, PROJECTS, STATUSES, TOOLS
from blog.demo_content import CATEGORIES, POSTS, TAGS
from blog.demo_posts_more import POSTS_MORE
from blog.models import Book, Category, Friend, Note, Post, Project, Status, Tag, ToolLink


class Command(BaseCommand):
    help = "Seed the site with demo articles, projects, notes and small content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-admin",
            action="store_true",
            help="Create a local admin account if it does not exist.",
        )
        parser.add_argument(
            "--admin-password",
            default=os.getenv("BLOG_ADMIN_PASSWORD"),
            help="Password for the demo admin account. If omitted, a random password is generated.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for row in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "name": row["name"],
                    "description": row["description"],
                    "icon": row["icon"],
                    "accent": row["accent"],
                    "order": row["order"],
                },
            )
            categories[row["slug"]] = category

        tags = {}
        for row in TAGS:
            tag, _ = Tag.objects.update_or_create(
                slug=row["slug"],
                defaults={"name": row["name"], "accent": row["accent"]},
            )
            tags[row["name"]] = tag

        posts = POSTS + POSTS_MORE
        for row in posts:
            post, _ = Post.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "title": row["title"],
                    "summary": row["summary"],
                    "content": row["content"],
                    "category": categories[row["category"]],
                    "status": Post.STATUS_PUBLISHED,
                    "is_featured": row.get("is_featured", False),
                    "cover_style": row["cover_style"],
                    "published_at": datetime.fromisoformat(row["published_at"]),
                    "views": row.get("views", 0),
                    "update_log": row.get("update_log", ""),
                    "errata": row.get("errata", ""),
                },
            )
            post.tags.set([tags[name] for name in row["tags"]])

        for row in PROJECTS:
            Project.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "title": row["title"],
                    "subtitle": row["subtitle"],
                    "summary": row["summary"],
                    "description": row["description"],
                    "category": row["category"],
                    "status": row["status"],
                    "progress": row["progress"],
                    "tech_stack": row["tech_stack"],
                    "repo_url": row["repo_url"],
                    "demo_url": row["demo_url"],
                    "cover_style": row["cover_style"],
                    "is_featured": row["is_featured"],
                    "sort_order": row["sort_order"],
                    "launched_at": date.fromisoformat(row["launched_at"]),
                },
            )

        for row in NOTES:
            note, _ = Note.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "title": row["title"],
                    "summary": row["summary"],
                    "body": row["body"],
                    "note_type": row["note_type"],
                    "aliases": row["aliases"],
                    "is_pinned": row["is_pinned"],
                },
            )
            note.tags.set([tags[name] for name in row["tags"]])

        for row in STATUSES:
            Status.objects.update_or_create(
                text=row["text"],
                defaults={
                    "mood": row["mood"],
                    "is_visible": True,
                    "created_at": timezone.now() - timedelta(days=row["days_ago"]),
                },
            )

        for row in FRIENDS:
            Friend.objects.update_or_create(
                url=row["url"],
                defaults={
                    "name": row["name"],
                    "description": row["description"],
                    "avatar_text": row["avatar_text"],
                    "accent": row["accent"],
                    "order": row["order"],
                    "is_visible": True,
                },
            )

        for row in BOOKS:
            Book.objects.update_or_create(
                title=row["title"],
                defaults={
                    "author": row["author"],
                    "category": row["category"],
                    "status": row["status"],
                    "rating": row["rating"],
                    "review": row["review"],
                    "accent": row["accent"],
                    "order": row["order"],
                },
            )

        for row in TOOLS:
            ToolLink.objects.update_or_create(
                url=row["url"],
                defaults={
                    "name": row["name"],
                    "description": row["description"],
                    "category": row["category"],
                    "icon": row["icon"],
                    "order": row["order"],
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(posts)} posts, {len(PROJECTS)} projects, {len(NOTES)} notes, "
                f"{len(BOOKS)} books and {len(TOOLS)} tools."
            )
        )

        if options["with_admin"]:
            User = get_user_model()
            username = "admin"
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(
                        "Admin account already exists; password was not changed."
                    )
                )
            else:
                password = options["admin_password"] or secrets.token_urlsafe(12)
                User.objects.create_superuser(
                    username=username,
                    email="admin@example.com",
                    password=password,
                    first_name="Site",
                    last_name="Admin",
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created admin account: {username} / {password}\n"
                        "Change this password immediately in /admin/ before any public deployment."
                    )
                )
