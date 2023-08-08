from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views import View
from users.forms import UserCreationForm, UserChangeForm, EmailLoginForm


class RegisterUserView(View):
    form_class = UserCreationForm
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'You were successfully registered.')
            return redirect('movies:index')
        return render(request, self.template_name, {'form': form})


# class LoginUserView(View):
#     form_class = AuthenticationForm
#     template_name = 'users/login.html'

#     def get(self, request):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request):
#         form = self.form_class(request, request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(username=username, password=password)
#             if user:
#                 login(request, user)
#                 messages.success(request, 'Welcome back to Cookie')
#                 return redirect('movies:index')
#         return render(request, self.template_name, {'form': form})

class LoginUserView(View):
    form_class = EmailLoginForm
    template_name = 'users/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back.')
                return redirect('movies:index')
        return render(request, self.template_name, {'form': form})


def logout_request(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('movies:index')


class ChangeUserView(View):
    form_class = UserChangeForm
    template_name = 'users/change_user.html'

    def get(self, request):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        current_user = request.user
        form = self.form_class(
            request.POST, instance=current_user)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                request, 'You successfully changed your credentials')
            return redirect('movies:index')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
