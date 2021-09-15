from bot.models import LogEntry
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

def logs(request):
    if (request.user.is_superuser):
        if request.method == 'GET':
            logs = LogEntry.objects.order_by('-id')
            log_strings = []
            for log in logs:
                log_strings.append(log.__str__())
            return JsonResponse({'logs': log_strings})
        if request.method == 'DELETE':
            LogEntry.objects.all().delete()
            return HttpResponse('Success')