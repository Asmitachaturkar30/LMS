from django.urls import path
from .views import * 

urlpatterns = [
#------------ AuctionSetup-------------------------------
    path('createAuction/',createAuction),
    path('getAllAuctions/', getAllAuctions),   
    path('updateAuction/<int:AuctionId>/',updateAuction),
    path('deleteAuction/<int:AuctionId>/',deleteAuction),
    path('getAuctionById/<int:AuctionId>/',getAuctionById),
]