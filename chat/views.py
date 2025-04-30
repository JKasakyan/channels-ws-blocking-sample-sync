from django.shortcuts import render

def chat_sync(request):
    return render(request, "chat/index_sync.html")