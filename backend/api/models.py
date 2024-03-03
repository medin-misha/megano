from django.db import models
from .utils import save_profile_avatar, save_product_image
from django.contrib.auth.models import User
import statistics, math

class Profile(models.Model):
    avatar = models.ImageField(null = True, blank=True, upload_to = save_profile_avatar)
    fullName = models.CharField(null = True, blank = False, max_length = 100)
    phone = models.IntegerField(null = True, blank = False)
    email = models.EmailField(null = True, blank = False)
    user = models.OneToOneField(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.fullName or self.pk

class Product(models.Model):
    category = models.IntegerField(default = 1)
    
    price = models.DecimalField(null = False, max_digits = 10, decimal_places = 2)
    available = models.BooleanField(default = True)
    count = models.IntegerField(default = 1)
    date = models.DateField(auto_now = True)
    title = models.CharField(null = False, blank = False, max_length = 100)
    description = models.TextField(null = True, blank = True, max_length = 10 ** 2)
    fullDescription = models.TextField(null = True, blank = True, max_length = 10 ** 5)

    freeDelivery = models.BooleanField(default = False)
    review_count = models.PositiveIntegerField(default = 0)
    rating = models.PositiveSmallIntegerField(default = 5)

    is_sale = models.BooleanField(default = False)
    salePrice = models.DecimalField(max_digits=10, decimal_places=2, null = True)
    dateForm = models.DateField(default = "1111-1-1", auto_now=False, auto_now_add=False)
    dateTo = models.DateField(default = "1111-1-1", auto_now=False, auto_now_add=False)
    is_limit = models.BooleanField(default = False)
    
    def __str__(self) -> str:
        return self.title or self.pk
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        reviews_count = len(self.reviews.all())

        self.review_count = reviews_count
        
        if reviews_count >= 1:
            self.rating = statistics.mean(
                [number.valuation for number in self.reviews.all()]
            ) if self.reviews.count() > 1 else self.reviews.all()[0].valuation
            print(self.rating)
        

class ProductImage(models.Model):
    src = models.ImageField(upload_to=save_product_image)
    alt = models.CharField(max_length = 100)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "images")

    def __str__(self):
        return self.src.url

class Tag(models.Model):
    name = models.CharField(null = False, max_length = 100)
    product = models.ManyToManyField(Product, related_name="tags")
    category = models.ForeignKey("CatalogItem", null = True, on_delete = models.SET_NULL, related_name = "tags")
    def __str__(self) -> str:
        return self.name
    
class Review(models.Model):
    autor = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "review")
    email = models.EmailField(null = True)
    text = models.TextField(null = False, blank = True, max_length = 5000)
    valuation = models.IntegerField(null = True)
    date = models.DateTimeField(auto_now_add = True)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "reviews")

    def __str__(self) -> str:
        return self.text
    
class SpecificationsProduct(models.Model):
    name = models.CharField(null = False, max_length = 50)
    value = models.CharField(null = True, max_length = 100)
    products = models.ManyToManyField(Product, related_name="specifications")

    def __str__(self) -> str:
        return self.name
    
class Basket(models.Model):
    user = models.OneToOneField(User, on_delete = models.SET_NULL, null = True, related_name = "basket")
    profile = models.ForeignKey(Profile, on_delete = models.CASCADE, null = True, related_name = "basket")
class BasketObject(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "basket_objects")
    count = models.PositiveIntegerField(default = 1)
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, related_name = "basket_objects")
    created_at = models.DateTimeField(auto_now_add = True)

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    profile = models.OneToOneField(Profile, on_delete = models.SET_NULL, null = True, related_name = "order")
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, related_name = "orders")

    fullName = models.CharField(null = True, max_length = 200)
    phone = models.IntegerField(null = True, blank = False)
    email = models.EmailField(null = True, blank = False)
    
    deliveryType = models.CharField(null = True, max_length = 15)
    paymentType = models.CharField(null = True, max_length = 15)
    totalCost = models.IntegerField(null = True)
    status = models.CharField(null = True, max_length = 15)
    city = models.CharField(null = True, max_length = 50)
    address = models.CharField(null = True, max_length = 200)
    products = models.ManyToManyField(BasketObject, related_name = "orders")

    def __str__(self):
        return f"{self.address}"

class CatalogItem(models.Model):
    title = models.CharField(null = False, max_length = 100)
    image = models.OneToOneField(ProductImage, null = True, on_delete = models.SET_NULL, related_name = "item")
class SubCatigory(models.Model):
    title = models.CharField(null = False, max_length = 100)
    image = models.OneToOneField(ProductImage, null = True, on_delete = models.CASCADE, related_name = "subitem")
    category = models.ForeignKey(CatalogItem, on_delete = models.CASCADE, related_name = "subcategories")
