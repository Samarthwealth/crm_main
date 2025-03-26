from django import forms
from .models import Sale
from .models import Client
from .models import User

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'amount', 'sale_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
        }

class FileUploadForm(forms.Form):
    file = forms.FileField()



class AddClientForm(forms.Form):
    name = forms.CharField(max_length=255, required=True, label="Client Name")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=15, required=True, label="Phone")
    pan = forms.CharField(max_length=10, required=False, label="PAN")  # Optional field
    relationship_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Relationship Managers"),
        required=False,
        label="Relationship Manager"
    )




class UpdateClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'pan', 'relationship_manager']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter client name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'pan': forms.TextInput(attrs={'placeholder': 'Enter PAN (optional)'}),
        }