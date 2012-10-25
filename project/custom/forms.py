from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EmailForm, self).__init__(*args, **kwargs)

    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save()

class SettingsForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    enable_facebook_updates = forms.BooleanField()
    enable_twitter_updates = forms.BooleanField()
    enable_email_updates = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SettingsForm, self).__init__(*args, **kwargs)

    def save(self):
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        self.user.save()

        profile = self.user.get_profile()
        profile.enable_facebook_updates = self.cleaned_data['enable_facebook_updates']
        profile.enable_twitter_updates = self.cleaned_data['enable_twitter_updates']
        profile.enable_email_updates = self.cleaned_data['enable_email_updates']
        profile.save()