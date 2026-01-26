from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .profile_models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name'
        })
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm Password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled widgets"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'phone', 'alternate_phone', 'address_line1', 'address_line2',
            'city', 'state', 'pincode', 'landmark', 'profile_image',
            'receive_offers', 'receive_updates'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number'
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Alternate Phone (Optional)'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Address Line 1'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Address Line 2 (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'PIN Code'
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Landmark (Optional)'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update user fields
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
            profile.save()
        
        return profile


from .models import Product, Category


class CategoryForm(forms.ModelForm):
    """Form for adding/editing categories"""
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Category Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'admin-input',
                'placeholder': 'Category Description',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'class': 'admin-input-file',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'admin-checkbox'
            }),
        }


class ProductForm(forms.ModelForm):
    """Form for adding/editing products"""
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'short_description',
            'price', 'discount_price', 'image', 'badge',
            'is_active', 'is_featured', 'stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(attrs={
                'class': 'admin-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'admin-input',
                'placeholder': 'Full Product Description',
                'rows': 5
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Short Description (max 255 chars)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Price (₹)',
                'step': '0.01'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Discount Price (₹) - Optional',
                'step': '0.01'
            }),
            'image': forms.FileInput(attrs={
                'class': 'admin-input-file',
                'accept': 'image/*'
            }),
            'badge': forms.Select(attrs={
                'class': 'admin-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'admin-checkbox'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'admin-checkbox'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'admin-input',
                'placeholder': 'Stock Quantity'
            }),
        }

