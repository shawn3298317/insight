from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    category = request.GET.get("category") # 0: cluster_map 1: heat_map
    time_start = request.GET.get("time_st")
    time_end = request.GET.get("time_end")
    center_lat = request.GET.get("c_lat")
    center_long = request.GET.get("c_long")

    return HttpResponse("Hello, world. You're at the folly index. The arguments are:\n"
                        "category = %s\ntime_start = %s\ntime_end = %s\ncenter_latitude = %s center_longtitude = %s"\
                        % (category, time_start, time_end, center_lat, center_long))

