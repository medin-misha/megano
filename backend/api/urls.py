from django.urls import path
from .views import RegisterApiView,ProductReview, TagsAPIView ,PaymantAPIView,CatigoriesAPIView, OrdersIdAPIView, OrdersAPIView, BasketAPIView, LogoutAPIView,ProductIdAPIView, LoginAPIView, ProfileAPIView, BannersAPIView, ProductlimitedAPIView, SaleAPIView, CatalogAPIView, ProductPopularAPIView
app_name = "api"

urlpatterns = [
    path("sign-up", RegisterApiView.as_view(), name = "register"),
    path("sign-in", LoginAPIView.as_view(), name = "login"),
    path("sign-out", LogoutAPIView.as_view(), name = "logout"), 
    
    path("profile", ProfileAPIView.as_view(), name="profile"),
    path("profile/avatar", ProfileAPIView.as_view(), name="avatar"),
    path("profile/password", ProfileAPIView.as_view(), name = "password"),
     
    path("banners", BannersAPIView.as_view(), name = "banners"),
    path("sales/", SaleAPIView.as_view(), name="sale"),
    path("catalog", CatalogAPIView.as_view(), name = "catalog"),
    path("products/popular", ProductPopularAPIView.as_view(), name="popular"),
    path("products/limited", ProductlimitedAPIView.as_view(), name="limited"),
    path("product/<int:pk>", ProductIdAPIView.as_view(), name="product_id"),
    path("product/<int:pk>/reviews", ProductReview.as_view(), name="create_review"),

    path("basket", BasketAPIView.as_view(), name="basket"),
    path("orders", OrdersAPIView.as_view(), name="orders"),
    path("order/<int:pk>", OrdersIdAPIView.as_view(), name="orderid"),
    path("payment/<int:id>", PaymantAPIView.as_view(), name = "paymant"),

    path("categories", CatigoriesAPIView.as_view(), name = "catigories"),
    path("tags", TagsAPIView.as_view(), name="tags"),

]