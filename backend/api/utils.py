from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from django.db import models
from django.core.paginator import Paginator
def get_data_from_request(request:Request) -> dict:
        """
            Функция, преобразующая 'сломанный' объект request.data в обычный словарь (dict).
            
            Параметры:
            - request: объект запроса (Request), от которого получаем данные.

            Возвращаемое значение:
            - data: словарь (dict), содержащий преобразованные данные из request.data.
        """
        data: dict = dict(request.data)
        for name in data:
            data: dict = eval(name)
            try:
                data["last_name"] = data["name"]
                data.pop("name")
            except:
                pass
            break;
        return data

def save_profile_avatar(instance, filename:str) -> str:
     return f"images/previews/{instance.pk}/{filename}"

def save_product_image(instance, filename:str) -> str:
     return f"images/product/{instance.product.pk}/{filename}"

def get_user_profile_info(user_profile) -> dict:
    user_avatar = user_profile.avatar or None
    data:dict = {
        "fullName":user_profile.fullName,
        "email":user_profile.email,
        "phone":user_profile.phone,
    }

    if user_avatar:
        data["avatar"] = {
            'src':user_avatar.url,
            "alt": "NONE",
        }
    return data

def is_valid_and_save(serializer:ModelSerializer) -> int:
     if serializer.is_valid():
          serializer.save()
          return True
     return False

def str_to_bool(string:str) -> bool:
     if string.lower == "false":
          return False
     else:
          return True

def get_paginate_data(paginator:Paginator, page:int, serializer:ModelSerializer) -> dict:
    page = paginator.page(page)
    return serializer(page.object_list, many = True)

