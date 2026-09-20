import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservationForm
from .models import Reservation, Table


def _selected_date_slot(request):
    today = datetime.date.today()
    date_str = request.GET.get('date') or today.isoformat()
    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError:
        date = today
    time_slot = request.GET.get('time', '19:00')
    valid_slots = dict(Reservation.TIME_SLOTS)
    if time_slot not in valid_slots:
        time_slot = '19:00'
    return date, time_slot


def table_map(request):
    date, time_slot = _selected_date_slot(request)
    tables = Table.objects.filter(is_active=True)
    occupied_ids = set(
        Reservation.objects.filter(date=date, time_slot=time_slot, status='confirmed')
        .values_list('table_id', flat=True)
    )
    for table in tables:
        table.occupied = table.id in occupied_ids

    return render(request, 'reservations/table_map.html', {
        'tables': tables,
        'date': date,
        'time_slot': time_slot,
        'time_slots': Reservation.TIME_SLOTS,
    })


@login_required
def reserve_table(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    date, time_slot = _selected_date_slot(request)

    if table.is_occupied_on(date, time_slot):
        messages.error(request, 'Цей столик уже заброньовано на обраний час.')
        return redirect(f"/reservations/?date={date}&time={time_slot}")

    initial = {
        'full_name': request.user.get_full_name() or request.user.username,
        'phone': getattr(request.user.profile, 'phone', ''),
        'date': date,
        'time_slot': time_slot,
    }

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            if table.is_occupied_on(form.cleaned_data['date'], form.cleaned_data['time_slot']):
                messages.error(request, 'Цей столик уже заброньовано на обраний час.')
            else:
                reservation = form.save(commit=False)
                reservation.table = table
                reservation.user = request.user
                reservation.save()
                messages.success(request, f'Столик №{table.number} заброньовано!')
                return redirect('reservations:my_reservations')
    else:
        form = ReservationForm(initial=initial)

    return render(request, 'reservations/reserve_form.html', {'form': form, 'table': table})


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('table')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.status = 'cancelled'
    reservation.save()
    messages.success(request, 'Бронювання скасовано.')
    return redirect('reservations:my_reservations')
