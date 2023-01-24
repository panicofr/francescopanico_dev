from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page
from wagtail.search import index
from wagtail.images.blocks import ImageChooserBlock

from wagtailcodeblock.blocks import CodeBlock


class HomePage(Page):
    author_name = models.CharField(max_length=30)
    tagline = models.CharField(max_length=100)
    bio = RichTextField(blank=True, features=["h2", "h3", "bold", "italic", "link"])

    content_panels = Page.content_panels + [
        FieldPanel("author_name"),
        FieldPanel("tagline"),
        FieldPanel("bio"),
    ]

    subpage_types = ["BlogPage", "PortfolioPage"]

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        context["latest_blog_posts"] = (
            BlogPostPage.objects.live().public().order_by("-first_published_at")[:3]
        )
        context["portfolio_posts"] = (
            PortfolioPostPage.objects.live()
            .public()
            .order_by("-first_published_at")[:4]
        )

        context["home_page"] = HomePage.objects.first()
        context["blog_page"] = BlogPage.objects.first()

        return context


class BlogPage(Page):
    subpage_types = ["BlogPostPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        all_posts = (
            self.get_children()
            .specific()
            .live()
            .public()
            .order_by("-first_published_at")
        )
        paginator = Paginator(all_posts, 1)
        page = request.GET.get("page")

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts
        print(list(posts))
        return context


class BlogPostPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    reading_minutes = models.PositiveIntegerField(default=5)

    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("code", CodeBlock(label="Code")),
        ],
        use_json_field=True,
    )

    parent_page_types = ["BlogPage"]

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("reading_minutes"),
        FieldPanel("feed_image"),
        FieldPanel("body"),
    ]


class PortfolioPage(Page):
    subpage_types = ["PortfolioPostPage"]


class PortfolioPostPage(Page):
    intro = models.CharField(max_length=250)
    github_link = models.URLField()

    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    parent_page_types = ["PortfolioPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("github_link"),
        FieldPanel("feed_image"),
    ]
