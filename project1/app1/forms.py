from django import forms
from .models import Expense, User

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class ExpenseForm(forms.ModelForm):
    SHARE_TYPE_CHOICES = [
        ('equally', 'Equally'),
        ('exactly', 'Exactly'),
        ('percentage', 'Percentage'),
    ]

    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    username = forms.CharField(label='Username', required=False)
    share_type = forms.ChoiceField(label='Sharing Type', choices=SHARE_TYPE_CHOICES)
    print('share ---',share_type)



    class Meta:
        model = Expense
        fields = ['username', 'amount', 'users', 'share_type']


       