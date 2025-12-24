from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json

from .forms import BookingForm
from .models import Menu, Booking

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import MenuSerializer, BookingSerializer


# -------------------- BASIC VIEWS --------------------

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def menu(request):
    menu_data = Menu.objects.all()
    return render(request, 'menu.html', {"menu": menu_data})

def display_menu_item(request, pk=None):
    menu_item = Menu.objects.get(pk=pk) if pk else None
    return render(request, 'menu_item.html', {"menu_item": menu_item})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'book.html', {'form': form})

def reservations(request):
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'reservations.html', {"bookings": booking_json})


# -------------------- AJAX / API BOOKING VIEW --------------------

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        exist = Booking.objects.filter(
            reservation_date=data['reservation_date'],
            reservation_slot=data['reservation_slot']
        ).exists()

        if exist:
            return JsonResponse({'error': 1})

        Booking.objects.create(
            first_name=data['first_name'],
            reservation_date=data['reservation_date'],
            reservation_slot=data['reservation_slot']
        )

        return JsonResponse({'success': 1})

    date = request.GET.get('date', datetime.today().date())
    bookings = Booking.objects.filter(reservation_date=date)
    booking_json = serializers.serialize('json', bookings)
    return HttpResponse(booking_json, content_type='application/json')


# -------------------- DRF API VIEWS --------------------

class MenuItemsView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
