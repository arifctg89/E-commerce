from django import forms

class CheckoutForm(forms.Form):
    # full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'John Doe'}))
    # email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'email@example.com'}))
    # address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '123 Python St, Code City'}))
    # phone = forms.CharField(max_length=20)


    full_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '123 Python St, Code City'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01XXXXXXXXX'})
    )