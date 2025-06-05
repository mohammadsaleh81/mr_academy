from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


tabs = [
    {
        "models": [
            "product.product",
        ],
        "items": [
            {
                "title": _("Mobile"),
                "link": lambda request: f"{reverse_lazy('admin:product_product_changelist')}?category__id__exact=2"

            },
            {
                "title": _("Accessory"),
                "link": lambda request: f"{reverse_lazy('admin:product_product_changelist')}?category__id__exact=4",

            },
            {
                "title": _("Tablet"),
                "link": lambda request: f"{reverse_lazy('admin:product_product_changelist')}?category__id__exact=3",

            },

        ],
    },
]


# def permission_callback(request):
#     return request.user.has_perm("sample_app.change_model")