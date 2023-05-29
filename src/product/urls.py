from django.urls import path
from product.views.product import CreateProductView, ProductListView, ProductAPIViewSet, ProductEditView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ProductListView.as_view(), name='list.product'),
    path('<int:id>/edit/', ProductEditView.as_view(), name='update.product'),

    # API URLs
    path('products/', ProductAPIViewSet.as_view({'post': 'create'}), name='api.product'),
]
