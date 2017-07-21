# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import smtplib
import json
import base64
import traceback
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import boto3

from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import urlencode

from .forms import ScriptForm
from .models import Script, SavedScripts, StarredScripts, ScriptFiles
from .models import ScriptRuns
# Create your views here.


def error_page(reuqest):
    return HttpResponseRedirect(_my_reverse(
        "pyfiddleweb:home", query_kwargs={
            "m": "Route not fiddled", "i": "true"}))


def success(reuqest):
    return HttpResponseRedirect(_my_reverse(
        "pyfiddleweb:home", query_kwargs={
            "m": "Thank you for your generosity"}))


def cancel(reuqest):
    return HttpResponseRedirect(_my_reverse(
        "pyfiddleweb:home", query_kwargs={
            "m": "Please donate next time"}))


def login(request):
    user = request.user
    if user.is_authenticated():
        return redirect(reverse('pyfiddleweb:home'))
    template = 'pyfiddleweb/home.html'
    context = _common_context
    return render(request, template, context)


def logout(request):
    auth_logout(request)
    return redirect(reverse('pyfiddleweb:home'))


def home(request):
    if request.method == "GET":
        template = 'pyfiddleweb/home.html'
        context = _common_context(request)
        context.update({
            'form': ScriptForm(),
            })
        if "i" in request.COOKIES:
            context.update({
                'i': "false"
            })
        else:
            context.update({
                'i': "true"
            })
        return render(request, template, context)


def fiddle(request, fiddle_id):
    if request.method == "GET":
        template = 'pyfiddleweb/home.html'
        try:
            script = Script.objects.get(id=fiddle_id, active=True)
            files = ScriptFiles.objects.filter(script_id=script.id)
        except ObjectDoesNotExist:
            print(traceback.print_exc())
            return HttpResponseRedirect(_my_reverse(
                "pyfiddleweb:home", query_kwargs={"m": "Could not find fiddle"}
                ))
        if script.private and script.user != request.user:
            return HttpResponseRedirect(
                    _my_reverse(
                        "pyfiddleweb:home",
                        query_kwargs={"m": "Not your fiddle to fiddle"}
                        )
                    )
        context = _common_context(request)
        context.update({
            'form': ScriptForm(instance=script),
            'script': script,
            'files': files,
            })
        if "i" in request.COOKIES:
            context.update({
                'i': "false"
            })
        else:
            context.update({
                'i': "true"
            })
        return render(request, template, context)


def run(request):
    if request.method == "POST" and request.is_ajax():
        try:
            payload = {}
            fiddle_id = request.POST.get("fiddle_id")
            version = request.POST.get("version", False)
            if fiddle_id:
                file_paths = ScriptFiles.objects.filter(script__id=fiddle_id)
                _get_s3_files(file_paths)
                files = {}
                for file_path in file_paths:
                    fil = open(
                        os.getenv("PYFIDDLE_WRITE_DIR")+file_path.name, "rb")
                    data = fil.read()
                    data_encoded = base64.b64encode(data)
                    files[file_path.name] = data_encoded
                payload["fiddle_id"] = fiddle_id
                payload["files_binary"] = files
                try:
                    script = Script.objects.get(id=fiddle_id)
                except Script.DoesNotExist:
                    print(traceback.print_exc())
                else:
                    if script.user != request.user:
                        script.runs += 1
                        script.save()
            code_entered = request.POST.get("code")
            csrftoken = request.COOKIES.get("csrftoken", " ")
            if code_entered == "":
                return JsonResponse({"error": "Please fiddle in some code"})
            else:
                ScriptRuns.objects.create(token=csrftoken, code=code_entered)
            payload["code"] = code_entered
            payload["commands"] = request.POST.get("commands", "")
            payload["packages"] = request.POST.get("packages", "")
            payload["inputs"] = request.POST.get("inputs", "")
            payload["token"] = csrftoken
            if version:
                function = os.getenv("EXECUTE_LAMBDA_36")
            else:
                function = os.getenv("EXECUTE_LAMBDA")
            client = boto3.client('lambda')
            print(function)
            print(json.dumps(payload))
            response = client.invoke(
                FunctionName=function,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload)
            )
            response_content = response["Payload"].read()
            response_json = json.loads(response_content)
            return JsonResponse(
                {
                    "output": response_json["body"]["message"],
                    "packages": response_json["body"]["packages"],
                    "statusCode": response["StatusCode"]
                }
            )
        except:
            print(traceback.print_exc())
            return JsonResponse(
                {"error": "Something went wrong"})
    else:
        return JsonResponse({"error": "Why are you here?"})


def save(request):
    if request.method == "POST" and request.is_ajax():
        if request.user.is_authenticated():
            fiddle_id = request.POST.get("fiddle_id")
            if fiddle_id:
                try:
                    script = Script.objects.get(id=fiddle_id, active=True)
                except Script.DoesNotExist:
                    return HttpResponseRedirect(
                            _my_reverse(
                                "pyfiddleweb:home",
                                query_kwargs={"m": "Could not find fiddle"},
                                )
                            )
                if script.user == request.user:
                    form = ScriptForm(instance=script, data=request.POST)
                    form.save()
                    return JsonResponse(
                            {"output": "", "message": "Updated Fiddle"})
                else:
                    saved_data = _save_new_fiddle(request)
                    if "fiddle_id" in saved_data:
                        status = _duplicate_files_for_save(
                            fiddle_id, saved_data["fiddle_id"])
                        if not status:
                            try:
                                Script.objects.get(
                                    id=str(saved_data["fiddle_id"])).delete()
                            except:
                                pass
                            return JsonResponse({
                                "message": "Could not save fiddle"})
                        if status:
                            return JsonResponse(saved_data)
                    else:
                        return JsonResponse(_save_new_fiddle(request))
            else:
                return JsonResponse(_save_new_fiddle(request))
        else:
            return JsonResponse(
                    {"output": "", "message": "Please login to Save a fiddle"})
    else:
        return JsonResponse({"output": "Why are you here?"})


def upload(request):
    fiddle_id = request.POST.get("fiddle_id")
    data = {}
    if fiddle_id:
        script = Script.objects.get(id=fiddle_id)
        if script.user != request.user:
            save_data = _save_new_fiddle(request, form_check=False)
            if "fiddle_id" in save_data:
                uploaded = _s3_upload(
                    request.FILES.getlist("upload"),
                    save_data['fiddle_id'])
                fiddle_id = save_data["fiddle_id"]
                data["fiddle_id"] = save_data["fiddle_id"]
        else:
            uploaded = _s3_upload(
                request.FILES.getlist("upload"),
                fiddle_id,
                )
    else:
        save_data = _save_new_fiddle(request, form_check=False)
        if "fiddle_id" in save_data:
            uploaded = _s3_upload(
                request.FILES.getlist("upload"), save_data['fiddle_id'])
            fiddle_id = save_data["fiddle_id"]
            data["fiddle_id"] = save_data["fiddle_id"]
    files = ScriptFiles.objects.filter(script__id=fiddle_id)
    data["files"] = []
    for fil in files:
        data["files"].append({"name": fil.name, "id": fil.id, })
    data["status"] = uploaded
    return JsonResponse(data)


def share(request):
    if request.method == "POST" and request.user.is_authenticated():
        return JsonResponse(_save_new_fiddle(request, save=False))
    if not request.user.is_authenticated():
        return JsonResponse({"message": "Please login to Share a fiddle"})
    else:
        return JsonResponse({"message": "Why are you here?"})


def star(request):
    if request.method == "POST" and request.user.is_authenticated():
        fiddle_id = request.POST.get("fiddle_id")
        try:
            script = Script.objects.get(id=fiddle_id, active=True)
        except Script.DoesNotExist:
            return JsonResponse({"message": "Could not find fiddle"})
        if script.private:
            return JsonResponse({"message": "Not your fiddle to fiddle"})
        StarredScripts.objects.create(
                script=script,
                user=request.user
                )
        return JsonResponse({"message": "Bookmarked fiddle"})
    if not request.user.is_authenticated():
        return JsonResponse({"message": "Please login to Star a fiddle"})
    else:
        return JsonResponse({"message": "Why are you here?"})


def delete(request):
    if request.method == "POST" and request.user.is_authenticated():
        fiddle_id = request.POST.get("fiddle_id", "")
        try:
            script = Script.objects.get(id=fiddle_id)
        except Script.DoesNotExist:
            return JsonResponse(
                {"status": 0, "message": "Could not find fiddle"})
        if script.user != request.user:
            return JsonResponse(
                {"status": 0, "message": "Not your fiddle to fiddle"})
        script.active = False
        script.save()
        return JsonResponse(
            {"status": 1, "message": "Fiddle fiddled out"})
    else:
        return JsonResponse(
            {"status": 0, "message": "Not your fiddle to delete"})


def file_delete(request):
    if request.method == "POST" and request.user.is_authenticated():
        fiddle_id = request.POST.get("fiddle_id")
        try:
            fil = ScriptFiles.objects.get(
                script_id=fiddle_id, id=request.POST.get("file_id"))
        except ScriptFiles.DoesNotExist:
            return JsonResponse({"status": 0})
        else:
            if fil.script.user != request.user:
                return JsonResponse({"status": 2})
            fil.delete()
            return JsonResponse({"status": 1})


def email_send(request):
    if request.method == "POST" and request.is_ajax():
        if request.POST.get("email") == "" or \
                request.POST.get("message") == "":
            return JsonResponse(
                {"message": "Please fill in email and message"})
        try:
            email_addr = request.POST.get("email", "")
            subject = request.POST.get("subject", "")
            message = request.POST.get("message", "")
            fromaddr = 'webmaster@pyfiddle.io'
            toaddr = 'webmaster@pyfiddle.io'
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "From Pyfiddle.io: "+subject

            body = "\n From: "+email_addr+"\n \nMessage: "+message
            msg.attach(MIMEText(body, 'plain'))
            username = os.getenv("PYFIDDLE_EMAIL")
            password = os.getenv("PYFIDDLE_EMAIL_PASS")
            server_ssl = smtplib.SMTP_SSL(
                "smtp.mail.us-east-1.awsapps.com", 465)
            server_ssl.ehlo()
            server_ssl.login(username, password)
            server_ssl.sendmail(fromaddr, toaddr, msg.as_string())
            return JsonResponse({"message": "Sent email"})
        except:
            print(traceback.print_exc())
            return JsonResponse({"message": "Error Sending Email"})
    else:
        return JsonResponse({"message": "Why are you here?"})


def privacy(request):
    template = "pyfiddleweb/privacy.html"
    return render(request, template, {})


def _common_context(request):
    most_runs = Script.objects.filter(
        runs__gte=5, active=True, private=False).order_by('-runs')[:10]
    context = {"most_runs": most_runs}
    if request.user.is_authenticated():
        saved_fiddles = SavedScripts.objects.filter(
            user=request.user, script__active=True)
        starred_fiddles = StarredScripts.objects.filter(
            user=request.user, script__active=True)
        context.update({
            "saved_fiddles": saved_fiddles,
            "starred_fiddles": starred_fiddles,
            })
    return context


def _my_reverse(viewname, kwargs=None, query_kwargs=None):
    url = reverse(viewname, kwargs=kwargs)
    if query_kwargs:
        return u'%s?%s' % (url, urlencode(query_kwargs))
    return url


def _save_new_fiddle(request, form_check=True, save=True):
    form = ScriptForm(data=request.POST)
    if form.is_valid():
        script_form = form.save(commit=False)
        script_form.user = request.user
        script_form.save()
        fiddle_id = script_form.id
        if save:
            SavedScripts.objects.create(
                    script_id=fiddle_id,
                    user=request.user,
                    )
        return {
                "output": "",
                "message": "Saved fiddle",
                "fiddle_id": fiddle_id,
                }
    else:
        if not form_check:
            fiddle = Script.objects.create(
                fiddle_name=request.POST.get("fiddle_name"),
                user=request.user,
                code=request.POST.get("code"),
                commands=request.POST.get("commands"),
                packages=request.POST.get("packages"),
                inputs=request.POST.get("inputs"),
                private=request.POST.get("private", False),
                version=request.POST.get("version", False)
            )
            fiddle_id = fiddle.id
            if save:
                SavedScripts.objects.create(
                        script_id=fiddle_id,
                        user=request.user,
                        )
            return {
                    "output": "",
                    "message": "Saved fiddle",
                    "fiddle_id": fiddle_id,
                    }
        data = {}
        data["output"] = ""
        data["errors"] = form.errors.as_json()
        return data


def _duplicate_files_for_save(old_fiddle_id, new_fiddle_id):
    try:
        old_files = ScriptFiles.objects.filter(script__id=str(old_fiddle_id))
        for old_file in old_files:
            ACCESS_KEY = os.getenv("PYFIDDLE_S3_KEY")
            SECRET_KEY = os.getenv("PYFIDDLE_S3_SECRET")

            session_get_files = boto3.Session(
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=os.getenv("PYFIDDLE_S3_REGION"),
            )

            s3 = session_get_files.resource('s3')
            copy_source = {
                'Bucket': os.getenv("PYFIDDLE_S3_BUCKET"),
                'Key': str(old_fiddle_id)+"/"+old_file.name
            }
            s3.meta.client.copy(
                copy_source,
                os.getenv("PYFIDDLE_S3_BUCKET"),
                str(new_fiddle_id)+"/"+old_file.name
            )
            ScriptFiles.objects.create(
                name=old_file.name,
                script_id=str(new_fiddle_id),
            )
    except:
        print(traceback.print_exc())
        return False
    else:
        return True


def _get_s3_files(file_paths):
    ACCESS_KEY = os.getenv("PYFIDDLE_S3_KEY")
    SECRET_KEY = os.getenv("PYFIDDLE_S3_SECRET")

    session_get_files = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=os.getenv("PYFIDDLE_S3_REGION"),
    )
    s3 = session_get_files.resource('s3')
    file_dir = os.getenv("PYFIDDLE_WRITE_DIR")
    for file_path in file_paths:
        s3.Bucket(
            os.getenv("PYFIDDLE_S3_BUCKET")).download_file(
                str(file_path.script.id)+"/"+file_path.name,
                file_dir+file_path.name
            )


def _s3_upload(files, fiddle_id):
    all_uploaded = True
    uploaded_files = []
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("PYFIDDLE_S3_KEY"),
            aws_secret_access_key=os.getenv("PYFIDDLE_S3_SECRET"),
            region_name=os.getenv("PYFIDDLE_S3_REGION"),
        )
        s3 = session.resource('s3')
        for fil in files[:10]:
            if fil.name not in uploaded_files and fil.size < 1200000:
                name = fil.name
                data = fil.read()
                s3.Bucket(
                    os.getenv('PYFIDDLE_S3_BUCKET')).put_object(
                        Key=str(fiddle_id)+"/"+name, Body=data)
                uploaded_files.append(name)
                ScriptFiles.objects.create(
                    script_id=str(fiddle_id),
                    name=name,
                )
    except:
        print(traceback.print_exc())
        all_uploaded = False
    return all_uploaded
