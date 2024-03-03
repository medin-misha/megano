from django.contrib import admin
from .models import Profile, Product, CatalogItem, SubCatigory, Order, ProductImage, Tag, Review, SpecificationsProduct, BasketObject

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class TagInline(admin.TabularInline):
    model = Tag.product.through
    extra = 1
class SpecificationsProductInline(admin.StackedInline):
    model = SpecificationsProduct.products.through
    extra = 1

class ProductInline(admin.TabularInline):
    model = Product.tags.through
    extra = 1
class SubCatigoryInline(admin.TabularInline):
    model = SubCatigory
    extra = 1

        
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display =  ("pk", "fullName", "email")
    list_display_links = list_display
    inlines = (ReviewInline, )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("pk", "count", "title", "price",  "freeDelivery","available",)
    list_display_links = list_display
    inlines = (ProductImageInline, TagInline, ReviewInline, SpecificationsProductInline)
    fieldsets = [
        ("main", {
           "fields":["title", "price", "count", "available", "description", "fullDescription", "category",]
        }),
        ('info & settings', {
           "fields":[ "freeDelivery", "review_count", "rating", ]
        }), 
        ("sale", {
            "fields":["is_sale","is_limit", "salePrice", "dateForm", "dateTo"]
        })
    ]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = (ProductInline,)
@admin.register(SpecificationsProduct)
class SpecificationsProductAdmin(admin.ModelAdmin):
    pass
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "created_at", "fullName", "phone", "address", "status", "city")
    list_display_links = list_display

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = "autor", "email", "valuation", "date", "product",
    list_display_links = list_display
@admin.register(BasketObject)
class BasketObjectAdmin(admin.ModelAdmin):
    pass



@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    inlines = (SubCatigoryInline, )