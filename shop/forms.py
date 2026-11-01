import re

from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="Họ và tên", max_length=100)
    phone = forms.CharField(label="Số điện thoại", max_length=20)
    address = forms.CharField(label="Địa chỉ giao hàng", max_length=255)
    cart_signature = forms.CharField(widget=forms.HiddenInput, required=False)
    submission_token = forms.UUIDField(widget=forms.HiddenInput)

    def clean_phone(self):
        phone = re.sub(r"[ .\-]", "", self.cleaned_data["phone"])
        if not re.fullmatch(r"0[0-9]{9}", phone):
            raise forms.ValidationError("Số điện thoại phải có 10 chữ số và bắt đầu bằng 0.")
        return phone
