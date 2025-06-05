from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from unfold_tools.sidebar import SIDEBAR
# from unfold_tools.tabs import tabs

UNFOLD = {
    # Site title and header
    "SITE_TITLE": "پنل مدیریت",
    "SITE_HEADER": "سیستم مدیریت محتوا",
    "SITE_URL": "/",

    # Icon and logo
    "SITE_ICON": lambda request: static("cropped-icon-2-192x192.webp"),
    "SITE_LOGO": lambda request: static("cropped-icon-2-192x192.webp"),

    # Display options
    "SHOW_HISTORY": True,  # Show "History" button
    "SHOW_VIEW_ON_SITE": True,  # Show "View on site" button

    # "ENVIRONMENT": "unfold_tools.utils.environment_callback",
    "DASHBOARD_CALLBACK": "unfold_tools.dashboard.dashboard_callback",

    # Login settings
    "LOGIN": {
        "image": lambda request: static("login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),  # Redirect to dashboard after login
    },

    # Custom styles and scripts (optional)
    # "STYLES": [
    #     lambda request: static("css/custom.css"),  # Add your custom CSS file
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/custom.js"),  # Add your custom JavaScript file
    # ],
    "BORDER_RADIUS": "20px",
    "COLORS": {
        "base": {
            "50": "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Enable search in sidebar
        "show_all_applications": False,
        "navigation": SIDEBAR
    },
    # "TABS": tabs
    "COMPONENTS": [
        {
            "name": "آمار کاربران",
            "template_name": "admin/dashboard/stats.html",
            "component": "unfold_tools.dashboard.UserStatsComponent",
            "columns": "full",
        },
        {
            "name": "آمار محتوا",
            "template_name": "admin/dashboard/content_stats.html",
            "component": "unfold_tools.dashboard.ContentStatsComponent",
            "columns": "full",
        },
        {
            "name": "نمودار فعالیت",
            "template_name": "admin/dashboard/graph.html",
            "component": "unfold_tools.dashboard.RecentActivityGraph",
            "columns": "full",
        },
    ],
}
