from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authentication import SessionAuthentication
from rest_framework import permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .filters import ProductFilter
from .serializers import UserSerializer, OrderSerializer, CatalogItemsSerializer, ProfileSerializer, ProductSerializer, BasketSerializer, SaleProductSerializer, ReviewSerializer, ProductIdSerializer
from .utils import get_data_from_request, get_user_profile_info, is_valid_and_save
from .models import Profile, Product, Basket, BasketObject, Order, CatalogItem

class RegisterApiView(APIView):

    authentication_classes = [SessionAuthentication]
    
    @transaction.atomic()
    def post(self, request:Request) -> Response:
        """
            Метод обработки HTTP POST-запроса для регистрации пользователя.

            Принимает данные запроса, выполняет регистрацию пользователя,
            возвращая токен при успешной регистрации и статус 200,
            или статус 400 при ошибке.

            :param request: Объект запроса (Request).
            :return: Ответ на запрос (Response).
        """
        data = get_data_from_request(request=request)
        user_serializer = UserSerializer(data = data)
        
        if is_valid_and_save(serializer = user_serializer):
            Profile.objects.create(
                user = user_serializer.instance,
                fullName = user_serializer.instance.username,
            )
            Basket.objects.create(
                user = user_serializer.instance
            )
            
            request.user = user_serializer.instance
            auth_user = authenticate(
                request = request,
                username = data.get("username"),
                password = data.get("password")
            )

            login(request=request, user = auth_user)
            return Response(status = 200)
        
        return Response(status = 400)
        
class LoginAPIView(APIView):
    """Метод обработки HTTP POST-запроса для аутентификации пользователя."""
    def post(self, request:Request):
        data = get_data_from_request(request=request)
        user = User.objects.get(username = data.get("username"))
        login(request = request, user = user )
        return Response({}, status=200)
        
class LogoutAPIView(APIView, IsAuthenticated):
    def post(self, request:Request) -> Response:
        """
            Метод обработки HTTP POST-запроса для выхода пользователя из аккаунта.
        """
        logout(request=request)
        return Response(status=200)

class ProfileAPIView(APIView, IsAuthenticated):
    
    def get(self, request:Request) -> Response:
        """Обработчик HTTP GET запроса для получения информации о профиле пользователя.

            Извлекает данные из профиля пользователя, включая полное имя, электронную почту и телефон.
            
            Возвращяет данные серверу в виде dict или json
        """
        user_profile = request.user.profile
        
        data = get_user_profile_info(user_profile = user_profile)
        return Response(
            data,
            status = 200
        )
    def post(self, request:Request) -> Response:
        """
        Обработка HTTP POST запроса для обновления профиля пользователя.

            Parameters:
                request (Request): HTTP запрос, содержащий данные пользователя.

            Returns:
                Response: HTTP ответ с соответствующим статусом.


            Данный метод принимает POST запросы для обновления профиля пользователя. Если в запросе 
            присутствует файл изображения "avatar", то обновляется аватар пользователя. Если файл не 
            передан, то обновляются остальные данные профиля, такие как полное имя ("fullName"), 
            телефон ("phone"), электронная почта ("email") аватар ("avatar").

            Если запрос успешно обработан, возвращается HTTP статус 200 OK с обновленными данными 
            профиля пользователя. Если произошла ошибка валидации данных или в запросе не было 
            передано ни одного поля, возвращается HTTP статус 400 Bad Request.
            """
            
       
        
        avatar = request.FILES.get("avatar") or None
        user_profile:Profile = request.user.profile
        data = request.data
        if avatar:  
                serializer = ProfileSerializer(instance = user_profile, data = {"avatar":avatar}, partial = True)
                if is_valid_and_save(serializer=serializer):
                    return Response(status = 200)
                return Response(status=400)
       


        elif data.get("currentPassword") or data.get("newPassword"):
           
            user = request.user
           
            new_password_data = {
                "password":data["newPassword"]
            }

            if user.check_password(request.data.get("currentPassword")): 
                serializer = UserSerializer(instance = user, data = new_password_data, partial = True)
                
                if is_valid_and_save(serializer=serializer):
                    login(request = request, user = user)
                    return Response(status = 200)
            return Response(status = 400)
        else:
            data = request.data
            data.pop("avatar")

            serializer = ProfileSerializer(instance = user_profile, data = data, partial = True)
            
            if is_valid_and_save(serializer = serializer):
                return self.get(request = request)
            
            return Response(status = 400)

class BannersAPIView(APIView):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки баннеров на главную страницу сайта.
        """
        
        banners = ProductSerializer(
            Product.objects.prefetch_related("tags", "images"), many = True
        )
        return Response(banners.data[:3], status = 200)
    
class SaleAPIView(APIView):

    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки товаров со скидкой.
        """
        page_number = request.GET.get("currentPage")

        paginator = Paginator(
                Product.objects.prefetch_related("images").filter(is_sale = True),
                10
            )
        

        serializer = SaleProductSerializer(paginator.page(page_number).object_list, many = True)
        result = {
            "items": [dict(item) for item in serializer.data],
            "currentPage":page_number,
            "lastPage":paginator.num_pages

        }

        return Response(result, status = 200)
    
class CatalogAPIView(APIView):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки и фильтрации товаров по критериям.
            
            "name": "string",
            "minPrice": 0,
            "maxPrice": 0,
            "freeDelivery": false,
            "available": true
            
        """
        params = dict(request.GET)
        filters_list = {}
        
        for key in params.copy().keys():
            if params[key][0] != '':
                params[key] = params[key][0] if not params[key][0].isdigit() else int(params[key][0])
            else:
                params.pop(key)
      
        for key in params.keys():
            if key.startswith("filter"):
                short_key = key[7:-1]
                if short_key == "name":
                    filters_list["title"] = params[key]
                elif short_key == "available":
                    if params[key] == "true":
                        filters_list[short_key] = True
                   
                elif short_key == "minPrice" or short_key == "maxPrice":
                    filters_list["price__range"] = (params["filter[minPrice]"], params["filter[maxPrice]"])
                elif short_key == "freeDelivery":
                   if params[key] == "true":
                        filters_list[short_key] = True
                else: 
                    filters_list[key] = params[key]
        print(filters_list)
        sorting_mode = "-" if params['sortType'] == "inc" else ""
        queryset = Product.objects.prefetch_related("images", "tags").order_by(f"{sorting_mode}{params['sort']}").filter(price__range = filters_list["price__range"])
        filterset = ProductFilter(
                data = filters_list,
                queryset = queryset
            )
        
        paginator = Paginator(
            filterset.qs,
            params["limit"]
        )
        serializer = ProductSerializer(
            paginator.page(params["currentPage"]).object_list,
            many = True
        )
        data = {
            "items":serializer.data,
            "currentPage":params["currentPage"],
            "lastPage": 1            
        }
        
        return Response(data = data,  status = 200)
    
class ProductPopularAPIView(APIView):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки товаров с самым лудшим рейтингом.
        """
        paginator = Paginator(
            Product.objects.prefetch_related("tags", "images").filter(rating__gt = 3),
            20
        )
        serializer = ProductSerializer(
                paginator.page(1).object_list, many = True
            )
        
        return Response(data = serializer.data, status=200)

class ProductlimitedAPIView(APIView):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки товаров с ограничиным тиражом.
        """
        paginator = Paginator(
            Product.objects.prefetch_related("tags", "images").filter(is_limit = True),
            20
        )
        
        serializer = ProductSerializer(
                paginator.page(1).object_list, many = True
            )
        
        return Response(data = serializer.data, status=200)

class ProductIdAPIView(APIView):
    def get(self, request:Request, pk:int) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки деталей товара по индексу pk.
        """
        serializer = ProductIdSerializer(instance = Product.objects.get(pk = pk), partial = True, many = False)
        
        return Response(serializer.data, status = 200)

class ProductReview(APIView, IsAuthenticated):

    def post(self, request:Request, pk:int) -> Response:
        """
            Метод обработки HTTP POSt-запроса для загрузки комметариев к товару (доработать к исправлению фронтенда).
        """
        print(request.POST.get("text"))
        data = dict(request.POST)
        data["product"] = pk
        serializer = ReviewSerializer(data = data)
        if is_valid_and_save(serializer=serializer):
            serializer = ProductIdSerializer(instance = Product.objects.get(pk = pk), partial = True, many = False)
            return Response(serializer.data, status = 200)
        return Response(status = 400)
    
class BasketAPIView(APIView, IsAuthenticated):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для загрузки корцины пользователя.
        """
        if isinstance(request.user, User):
            user = request.user
            basket, basket_is_create = Basket.objects.get_or_create(user = user)
            basket_serializer = BasketSerializer(instance = basket)
            
            return Response(data = basket_serializer.data["basket_objects"][::-1], status = 200)
        else:
            return Response({"user":"Anonimus"}, status = 200)
    def post(self, request:Request) -> Response:
        """
            Метод обработки HTTP POST-запроса для создания карцины пользователя.
        """
        product_instance = Product.objects.prefetch_related("images","tags").get(
                    pk = request.data['id']
                )
        basket, basket_is_create = Basket.objects.get_or_create(user = request.user)
        
        basket_object, basket_object_is_create = BasketObject.objects.get_or_create(
            basket = basket, product = product_instance
        )
        
        if not basket_object_is_create:
            basket_object.count += request.data["count"]
            basket_object.save()
        else:
            basket_object.count = request.data["count"]
            basket_object.save()
            
        user = request.user
        basket, basket_is_create = Basket.objects.get_or_create(user = user)
        basket_serializer = BasketSerializer(instance = basket)
        data = basket_serializer.data["basket_objects"]
        return Response(data = data, status = 200)
    
    def delete(self, request:Request):
        """
            Метод обработки HTTP DALETE-запроса для удаления обьекта из козины
        """
        basket = request.user.basket
        data = request.data
        basket_object = basket.basket_objects.get(product__id = data["id"])
        if basket_object.count == data['count']:
            basket_object.delete()
        else:
            basket_object.count = basket_object.count - data['count']
            basket_object.save()
        basket_serializer = BasketSerializer(instance = basket)
        data = basket_serializer.data["basket_objects"]
        return Response(data = data, status = 200)
        
class OrdersAPIView(APIView, IsAuthenticated):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для получает все заказы.
        """
        orders = Order.objects.prefetch_related("products", "profile").all()
        order_serializer = OrderSerializer(orders, many = True)
        return Response(order_serializer.data, status = 200)
    
    @transaction.atomic
    def post(self, request:Request):
        """
            Метод обработки HTTP POST-запроса для создания заказа отдельного пользователя.
        """
        basket_objects = BasketObject.objects.filter(basket = request.user.basket)
        order, order_is_create = Order.objects.get_or_create(
            
            profile = request.user.profile,
        )
        if order_is_create:
            order.products.set(basket_objects)
        total_price = sum(
                [product.product.price for product in order.products.prefetch_related("product").all()]
            )
        order.totalCost = total_price
        order.save()
        
        return Response({"orderId":order.pk}, status = 200)

class OrdersIdAPIView(APIView, IsAuthenticated):
    def get(self, request:Request, pk:int)-> Response:
        """
            Метод обработки HTTP GET-запроса для получения по ID заказа и вывода по ниму информации.
        """
        order = get_object_or_404(Order, pk = pk)
        order_serializer = OrderSerializer(instance = order)
        return Response(order_serializer.data, status = 200)
    
    
    def post(self, request:Request, pk:int) -> Response:
        """
            Метод обработки HTTP POST-запроса для измениния заказа по пользовательским данным.
        """
        data = {
            "fullName": request.data["fullName"],
            "phone":request.data["phone"] if request.data["phone"].isdigit() else 0,
            "email":request.data["email"],
            "deliveryType":request.data["deliveryType"],
            "city":request.data["city"],
            "address":request.data["address"],
            "paymentType":request.data["paymentType"],
            "status":request.data["status"],
            "totalCost":request.data["totalCost"],

        }
        
        order_serializer = OrderSerializer(
            instance = Order.objects.get(pk = pk)
        )
        order_serializer.update(instance = order_serializer.instance, validated_data = data).save()

        return Response({"orderId":order_serializer.instance.pk}, status = 200)
 
class PaymantAPIView(APIView, IsAuthenticated):
    def post(self, request:Request, id:int) -> Response:
        """
            Метод обработки HTTP POST-запроса для оплаты заказа и его маркировки как оплаченый.
            Так же отсойденяет его от пользователя что бы он мог создать новый заказ
        """
        basket = request.user.basket
        order = Order.objects.get(pk = id)
            
        if int(request.data["number"]) % 2 == 0 and int(request.data["number"]) % 10 != 0:
            order.status = "accepted"
            order.profile = None
            order.user = request.user
            basket.user = None
            basket.profile = request.user.profile
           
            basket.save()
            order.save()
            return Response(status = 200)
        order.status = 'failed'
        return Response(status=400)

class CatigoriesAPIView(APIView):
    def get(self, request:Request) -> Response:
        """
            Метод обработки HTTP GET-запроса для получения катигорий.
        """
        item_serializer = CatalogItemsSerializer(
            CatalogItem.objects.prefetch_related("subcategories", "image"), many = True
        )
        return Response(data = item_serializer.data, status = 200)

class TagsAPIView(APIView):
    
    def get(self, request:Response):
        """
            Метод обработки HTTP GET-запроса для получения тегов отдельной категории.
        """
        print(int(request.GET.get("category")[0]))
        instance = get_object_or_404(CatalogItem, pk = int(request.GET.get("category")[0]) )
        item_serializer = CatalogItemsSerializer(
            instance = instance
        )
        
        return Response(item_serializer.data, status = 200)


















