from django import forms
from models import RegisteredDevicePublicKey, Zone, FacilityUser, Facility, FacilityGroup

class RegisteredDevicePublicKeyForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(RegisteredDevicePublicKeyForm, self).__init__(*args, **kwargs)
        if not user.is_superuser:
            self.fields['zone'].queryset = reduce(lambda x,y: x+y,
                [orguser.get_zones() for orguser in user.organizationuser_set.all()])

    class Meta:
        model = RegisteredDevicePublicKey
        fields = ("zone", "public_key",)


class FacilityUserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, label="Password")    
    
    def __init__(self,request,*args,**kwargs):
        self.request = request
        super(FacilityUserForm,self).__init__(*args, **kwargs)
    
    class Meta:
        model = FacilityUser
        fields = ("group", "username", "first_name", "last_name",)

    def clean(self):
        username = self.cleaned_data.get('username')
        facility = self.cleaned_data.get('facility')
        
        if FacilityUser.objects.filter(username=username, facility=facility).count() > 0:
            raise forms.ValidationError("A user with this username at this facility already exists. Please choose a new username and try again.")

        return self.cleaned_data

    
class FacilityTeacherForm(FacilityUserForm):

    class Meta:
        model = FacilityUser
        fields = ("username", "first_name", "last_name",)

class FacilityForm(forms.ModelForm):

    class Meta:
        model = Facility
        fields = ("name", "description", "address", "address_normalized", "latitude", "longitude", "zoom")

        
class FacilityGroupForm(forms.ModelForm):

    class Meta:
        model = FacilityGroup
        fields = ("name",)
    

class LoginForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = FacilityUser
        fields = ("facility", "username", "password")

    def __init__(self, request=None, *args, **kwargs):
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['facility'].queryset = Facility.objects.all()


    def clean(self):
        username = self.cleaned_data.get('username')
        facility = self.cleaned_data.get('facility')
        password = self.cleaned_data.get('password')

        try:
            self.user_cache = FacilityUser.objects.get(username=username, facility=facility)
        except FacilityUser.DoesNotExist as e:
            raise forms.ValidationError("User not found. Did you type your username correctly, and choose the right facility?")
        
        if not self.user_cache.check_password(password):
            self.user_cache = None
            if password and "password" not in self._errors:
                self._errors["password"] = ["Password was incorrect."]
        
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

# class OrganizationForm(forms.ModelForm):
#     class Meta:
#         model = Organization
#         fields = ("name", "description", "url",)
#         widgets = {
#             "name": forms.TextInput(attrs={"size": 70}),
#             "description": forms.Textarea(attrs={"cols": 74, "rows": 2}),
#             "url": forms.TextInput(attrs={"size": 70}),
#         }

