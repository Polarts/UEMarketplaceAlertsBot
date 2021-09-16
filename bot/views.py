from bot.models import AppState, LogEntry
from django.http import JsonResponse, HttpResponse

def logs(request):
    if (request.user.is_superuser):
        if request.method == 'GET':
            logs = LogEntry.objects.order_by('-id')
            log_dicts = []
            for log in logs:
                log_dicts.append(log.to_dict())
            return JsonResponse({'logs': log_dicts})
        if request.method == 'DELETE':
            LogEntry.objects.all().delete()
            return HttpResponse('Success')

def set_app_state(request, newState):
    if (request.user.is_superuser):
        state = AppState.objects.get(pk=1)
        if state.play_state == AppState.PlayStates.STOP \
           and state.health_state == AppState.HealthStates.BAD:
            state.health_state = AppState.HealthStates.PENDING
        state.play_state = newState
        state.save()
        return HttpResponse('Success')

def get_app_state(request):
    if (request.user.is_superuser):
        state = AppState.objects.get(pk=1)
        return JsonResponse(state.to_dict())