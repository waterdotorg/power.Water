from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EmailForm, self).__init__(*args, **kwargs)

    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save()