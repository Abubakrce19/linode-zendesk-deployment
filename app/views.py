from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.views.generic import FormView
from django.urls import reverse
import json 
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from .decorators import only_authenticated_user, redirect_authenticated_user
import json
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
import os 
import re 
import requests
from django.contrib.staticfiles.views import serve as static_serve
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import (Docs)
from users.models import CustomUser


def generate_gpt(text, history=[]):
        headers = {"Authorization": f"Bearer {settings.EDEN_AI_API_KEY}"}
        url ="https://api.edenai.run/v2/text/chat"
        payload = {
            "providers": "openai",
            "text": text,
            "chat_global_action": "Follow user instructions",
            "previous_history" : history,
            "temperature" : 0.0,
            "settings":{"openai":"gpt-3.5-turbo"},
            "max_tokens" : 1000
            }
        response = requests.post(url, json=payload, headers=headers)
        try:
            result = json.loads(response.text)
            msg = result['openai']['generated_text']
            # print(msg)
        except Exception as e:
            return 
        return msg
    

class Onboard(View):
    template = "onboard.html"
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.token != None:
            return redirect('app:dashboard')

        context = {
            "user": user
        }
        return render(self.request, self.template, context)
    

def get_creds(user):
        # creds = {
    #     'email' : "abhi22@skiff.com",
    #     'token' : 'PvrVLyjWWagOP0EeHA8RZeaZxwmdzi9rP0S3yGOr',
    #     'subdomain': 'skiff5911'
    # }
    
    creds = {
        'email' : user.email,
        'token' : user.token,
        'subdomain': user.subdomain
    }
    return creds


class Setup_user(View):
    def post(self, request):
        from .core_pipeline import build_embeddings, main_pipeline
        data = json.loads(request.body)
        user = request.user 
        user.token = data['token']
        user.subdomain = data['subdomain']
        user.save()

        creds = get_creds(user)
        build_embeddings(creds, user.id)
        return JsonResponse({'result': True})


# Main Dashboard for the chat UI 
class Dashboard(View):
    template = "dashboard.html"
    def get(self, request, id=None, *args, **kwargs):
        user = request.user

        docs = Docs.objects.filter(user=user)

        context = {
            "user": user, 
            "docs": docs,
        }

        if id:
            doc = Docs.objects.filter(id=id).first()
            messages = doc.messages
            if messages:
                messages = eval(doc.messages)
            else:
                messages = []
            print(type(messages))
            context = {
                "user": user, 
                "docs": docs,
                "messages": messages,
                "show_context": True,
                "parent_id": id
            }

        return render(self.request, self.template, context)
    

# Main chat endpoint 
class Chat(View):
    def post(self, request):
        from .core_pipeline import build_embeddings, main_pipeline
        data = json.loads(request.body)
        user = request.user 


        if data.get('id') == None:
            doc = Docs.objects.create(user=request.user)
            doc.save()
            return JsonResponse({'id': doc.id, 'status': True})
        else:
            if user.docs_left == 0:
                return JsonResponse({'error': 'You have used all your remaining query, please upgrade.'})

            creds = get_creds(user)
            user_msg = data['query_txt']
            output = main_pipeline(creds, user_msg, user.id)

            doc = Docs.objects.filter(id=data['id']).first()
            if doc.messages:
                messages = eval(doc.messages) 
                messages.append({"user_msg": user_msg})
                messages.append({"bot_response": output})
            else:
                messages = []
                messages.append({"user_msg": user_msg})
                messages.append({"bot_response": output})   
                   
            doc.messages = str(messages)
            doc.save() 

            user.docs_left = user.docs_left - 1
            user.save()

        return JsonResponse({'msg': output, 'status': True})


class UserProfile(View):
    template = "user_profile.html"
    def get(self, request, *args, **kwargs):
        return render(self.request, self.template)
    

# updates user profile 
class Update_profile(View):
    def post(self, request):
        data = json.loads(request.body)
        user = request.user 
        user.first_name = data['first_']
        user.last_name = data['sec_']
        user.email = data['email']
        user.save()
        return JsonResponse({'result': True})


# updates the database by fetching & building newer tickets 
class Update_db(View):
    def post(self, request):
        from .core_pipeline import build_embeddings, main_pipeline
        data = json.loads(request.body)
        user = request.user 

        creds = get_creds(user)
        build_embeddings(creds, user.id)
        return JsonResponse({'result': True})

