from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from .models import Profile, Product, Order, CatalogItem, SubCatigory, ProductImage,Basket, Tag, Review, SpecificationsProduct, BasketObject

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["last_name", "username", "password"]

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar", "fullName", "phone", "email", "user"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["pk", "alt", "src"]

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "pk", "name"
        ]

class SpecificationsProductSerializer(ModelSerializer):
    class Meta:
        model = SpecificationsProduct
        fields = ["pk", "name", "value"]

class ReviewSerializer(ModelSerializer):
    rate = serializers.IntegerField(source = "valuation", max_value = 5, min_value = 1)
    class Meta:
        model = Review
        fields = [
            "pk","autor", "email", "text", "rate", "date", "product"
        ]

class ProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many = True)
    tags = TagSerializer(many = True)
    reviews = serializers.IntegerField(source = "review_count")
    class Meta:
        model = Product 
        fields = [
                  "id", "category", "price", "count", 
                  "date", "title", "description", 
                  "freeDelivery", "review_count", "rating", 
                  "images", "tags", "reviews"
                ]

class SaleProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many = True)
    class Meta:
        model = Product
        fields = [
            "id", "price", "salePrice",
            "dateForm", "dateTo", "title",
            "images", 
        ]
   
class ProductIdSerializer(ModelSerializer):

    images = ProductImageSerializer(many = True)
    tags = serializers.StringRelatedField(many = True)
    reviews = ReviewSerializer(many = True)
    specifications = serializers.ManyRelatedField(child_relation=SpecificationsProductSerializer())

    class Meta:
        model = Product
        fields = [ 
          
            "id", "category", "price",
            "count", "date", "title",
            "description", "fullDescription", "freeDelivery",
            "images", "tags",  "specifications", "reviews",
            "rating",
        ]

class BasketObjectSerializer(ModelSerializer):
    product = ProductSerializer(many = False)
    class Meta:
        model = BasketObject
        fields = ["product",]
        ordering = ["created_at"]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product"]["count"] = instance.count
        new_data = data["product"]
        return new_data

class BasketSerializer(ModelSerializer):
    basket_objects = BasketObjectSerializer(many = True)
    class Meta:
        model = Basket
        fields = ["basket_objects"]
       
class OrderProfileSerializer(ModelSerializer):
    
    class Meta:
        model = Profile
        fields = [
            "fullName", "email", "phone"

        ]

class OrderSerializer(ModelSerializer):
    profile = OrderProfileSerializer()
    products = BasketObjectSerializer(many = True)
    class Meta:
        model = Order
        fields = [
            "id","created_at", "fullName", "email", 
            "phone","deliveryType", "paymentType", 
            "totalCost", "status", "city",
            "address","products", "profile"
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(data)

        return data 
    
class SubCatigorySerializer(ModelSerializer):
    class Meta:
        model = SubCatigory
        fields = "id", "title", "image"

class CatalogItemsSerializer(ModelSerializer):
    image = ProductImageSerializer()
    subcategories = SubCatigorySerializer(many = True)
    tags = serializers.StringRelatedField(many = True)
    class Meta:
        model = CatalogItem
        fields = [
            "id", "title", "image", "subcategories", "tags"
        ]



