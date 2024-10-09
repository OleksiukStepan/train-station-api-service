from django.contrib import admin

from train_station.models import (
    Crew,
    Route,
    Order,
    Ticket,
    Train,
    TrainType,
    Station,
    Journey,
)


admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Ticket)
