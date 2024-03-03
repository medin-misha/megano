from django.forms import ModelForm

class UserModelForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "password"]