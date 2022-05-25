from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
# Create your views here.
import datetime
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template import loader
from .utils.charts import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict
from .forms import CreateUserForm
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from .models import Transaction, User, Category
from django.template import RequestContext
from django.db.models import Sum
from .forms import FilterForm, FilterFormDate
from django.shortcuts import redirect

def home(request):
    template = loader.get_template('budzetapp/home.html')
    return render(request, 'budzetapp/home.html')


def userInterface(request):
    template = loader.get_template('budzetapp/userInterface.html')
    return render(request, 'budzetapp/userInterface.html')


def przychody(request):
    if request.method == 'POST':
        if request.POST.get('sum') and request.POST.get('category'):
            transaction = Transaction()
            transaction.type = 'przychody'
            transaction.sum = request.POST.get('sum')
            transaction.category = Category()
            transaction.category.name = request.POST.get('category')
            transaction.user = request.user
            transaction.category.save()
            transaction.save()

            return render(request, 'budzetapp/przychody.html')

    else:
        return render(request, 'budzetapp/przychody.html')


def wydatki(request):
    if request.method == 'POST':
        if request.POST.get('sum') and request.POST.get('category'):
            transaction = Transaction()
            transaction.type = 'wydatki'
            transaction.sum = request.POST.get('sum')
            transaction.category = Category()
            transaction.category.name = request.POST.get('category')
            transaction.user = request.user
            if request.POST.get('date'):
                transaction.trans_date = request.POST.get('date')
            transaction.category.save()
            transaction.save()

            return render(request, 'budzetapp/wydatki.html')

    else:
        return render(request, 'budzetapp/wydatki.html')


def wykresy_filtrowanie(request):
    template = loader.get_template('budzetapp/wykresy_filtrowanie.html')
    return render(request, 'budzetapp/wykresy_filtrowanie.html')


def transakcje(request):
    template = loader.get_template('budzetapp/transakcje.html')
    listaTransakcji = Transaction.objects.filter(user=request.user)
    return render(request, 'budzetapp/transakcje.html', {"listaTransakcji": listaTransakcji})


class wykresslupkowy(TemplateView):
    template_name = 'budzetapp/wykresslupkowy.html'
    form_class = FilterFormDate

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return render(request, 'budzetapp/wykresslupkowywykres.html',
                          {'qs': Transaction.objects.filter(user=self.request.user,
                                                            trans_date__gte=form.cleaned_data['date1'],
                                                            trans_date__lte=form.cleaned_data['date2'])})

        return render(request, '/budzetapp/wykresslupkowy')

    def get_context_data(self, **kwargs):
        context = super(wykresslupkowy, self).get_context_data(**kwargs)

        if self.request.method == 'POST':
            form = FilterFormDate(self.request.POST)
        else:
            form = FilterFormDate()
        context["form"] = form
        if form.is_valid():
            context["qs"] = Transaction.objects.filter(user=self.request.user,
                                                       trans_date__gte=form.cleaned_data['date1'],
                                                       trans_date__lte=form.cleaned_data['date2'])
        else:
            context["qs"] = Transaction.objects.all()
        return context
    # template = loader.get_template('budzetapp/wykreskolowy.html')
    # return render(request, 'budzetapp/wykreskolowy.html')


class wykreskolowy(TemplateView):
    template_name = 'budzetapp/wykreskolowy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs"] = Transaction.objects.filter(user=self.request.user)
        transakcjeWydatkow = Transaction.objects.filter(user=self.request.user, type="wydatki")
        Wydatki = transakcjeWydatkow.aggregate(Sum('sum'))
        transakcjePrzychodow = Transaction.objects.filter(user=self.request.user, type="przychody")
        Przychody = transakcjePrzychodow.aggregate(Sum('sum'))
        sumaWydatkow = Wydatki['sum__sum']
        sumaPrzychodow = Przychody['sum__sum']
        context.update({'sumaWydatkow': sumaWydatkow, 'sumaPrzychodow': sumaPrzychodow})
        print("wydatki: ", sumaWydatkow)
        print("przychody: ", sumaPrzychodow)
        return context
    # template = loader.get_template('budzetapp/wykreskolowy.html')
    # return render(request, 'budzetapp/wykreskolowy.html')


def transakcjefiltrowanie(request):
    if request.method == 'POST':
        form = FilterForm(request.POST)
    else:
        form = FilterForm()

    if form.is_valid():
        template = loader.get_template('budzetapp/transakcjefiltrowanie.html')
        listaTransakcji = Transaction.objects.filter(user=request.user)
        if Transaction.objects.filter(category__name=form.cleaned_data['category']).count() == 0:
            return render(request, 'budzetapp/transakcjefiltrowanie.html',
                          {"form": FilterForm, "output": form.cleaned_data['category']})
        return render(request, 'budzetapp/transakcjefiltrowanie.html',
                      {"form": FilterForm, "output": form.cleaned_data['category'], "listaTransakcji": listaTransakcji})
    template = loader.get_template('budzetapp/transakcjefiltrowanie.html')
    listaTransakcji = Transaction.objects.all()
    return render(request, 'budzetapp/transakcjefiltrowanie.html', {"form": FilterForm})


def transakcjefiltrowaniedatapomiedzy(request):
    if request.method == 'POST':
        form = FilterFormDate(request.POST)
    else:
        form = FilterFormDate()
    if form.is_valid():
        print("data1", form.cleaned_data['date1'])
        print("data2", form.cleaned_data['date2'])
        template = loader.get_template('budzetapp/transakcjefiltrowaniedatapomiedzy.html')
        listaTransakcji = Transaction.objects.filter(user=request.user, trans_date__gte=form.cleaned_data['date1'],
                                                     trans_date__lte=form.cleaned_data['date2'])
        if Transaction.objects.filter(trans_date__gte=form.cleaned_data['date1'],
                                      trans_date__lte=form.cleaned_data['date2']).count() == 0:
            return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html',
                          {"form": FilterFormDate, "data1": form.cleaned_data['date1'],
                           "data2": form.cleaned_data['date2']})
        return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html',
                      {"form": FilterFormDate, "data1": form.cleaned_data['date1'], "data2": form.cleaned_data['date2'],
                       "listaTransakcji": listaTransakcji})
    template = loader.get_template('budzetapp/transakcjefiltrowaniedatapomiedzy.html')
    listaTransakcji = Transaction.objects.all()
    return render(request, 'budzetapp/transakcjefiltrowaniedatapomiedzy.html', {"form": FilterFormDate})


from .forms import LoginForm


def get_name(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = LoginForm()

    return render(request, 'name.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['email']
    form = LoginForm()
    return render(request, 'budzetapp/userInterface.html', {'form': form})


def createTransaction(request):
    if request.method == 'POST':
        if request.POST.get('type') and request.POST.get('sum') and request.POST.get('category'):
            transaction = Transaction()
            transaction.type = request.POST.get('type')
            transaction.sum = -request.POST.get('sum')
            transaction.category = request.POST.get('category')
            transaction.user = User.objects.filter(pk=1)
            transaction.save()

            return render(request, 'budzetapp/userInterface.html')

    else:
        return render(request, 'budzetapp/userInterface.html')


def rejestracja(request):
    form = CreateUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return render(request, 'budzetapp/userInterface.html', {"form": form})
    return render(request, 'budzetapp/rejestracja.html', {"form": form})


def wykresslupkowywykres(request):
    qs = Transaction.objects.filter(user=request.user,
                                    trans_date__gte=request.data1,
                                    trans_date__lte=request.data2)
    return render(request, 'budzetapp/wykresslupkowywykres.html', qs)
