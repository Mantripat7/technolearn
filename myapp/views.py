from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, FileResponse,HttpResponse
from django.contrib import messages
from myapp.models import *
import stripe
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter, legal, landscape, portrait
from openai import OpenAI
from google import genai
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, letter, legal, landscape, portrait
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
import io
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.core.files.base import ContentFile
from django.core.mail import send_mail
import random
import string
from fpdf import FPDF
import re

stripe.api_key = settings.STRIPE_SECRET_KEY


def faq(request):
    if request.session.get('Email'):
        email=request.session.get('Email')
        user  = get_object_or_404(Userregister, email = email)
    else:
        user=False
        email=False
    return render(request,'faq.html' , {'user': user, 'email':email})


def login(request):
    if request.method == "POST":
        email = request.POST.get('em', '').strip()
        password = request.POST.get('pw', '')
    
        user_qs = Userregister.objects.filter(email=email, password=password)
        
        if user_qs.exists():
          
            request.session['Email'] = email
            return redirect('index')
        else:
            messages.success(request, "Invalid Credentials.")
            return redirect('login')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        name = request.POST.get('nm', '').strip()
        email = request.POST.get('em', '').strip().lower()
        password = request.POST.get('pw', '')
        confirm  = request.POST.get('cpw', '')

        if not (name and email and password and confirm):
            return render(request, 'register.html', {
                'msg': "All fields are required.",
                'name': name,
                'email': email,
            })

        if password != confirm:
            return render(request, 'register.html', {
                'msg': "Password and confirm password do not match.",
                'name': name,
                'email': email,
            })

        # Check for duplicate email
        if Userregister.objects.filter(email=email).exists():
           
            return render(request, 'register.html', {
                'msg': "Email ID already exists.",
                'name': name,
            })

        new_user = Userregister(
            name=name,
            email=email,
            password=password 
        )
        new_user.save()

        return render(request, 'login.html', {
            'msg': "Registered successfully, Now you can login"
        })

    return render(request, 'register.html')


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.module_set.all()
    request.session['course_id'] = course_id
    user_has_purchased = False
    email = request.session.get('Email')

    user_certified =False
    if email:
        user  = get_object_or_404(Userregister, email=email)
        user_certified =  modules.count() == LessonTestResult.objects.filter(user=user, course=course).count()
        try:
            user_record = Userregister.objects.get(email=email)
            user_has_purchased = user_record.purchase_courses.filter(id=course.id).exists()
            print(user_has_purchased)
        except Userregister.DoesNotExist:
            return redirect('login')

    template_name = 'courses_detail_enroll.html' if user_has_purchased else 'courses_detail.html'
    context = {
        'course': course,
        'email': email,
        'modules': modules,
        'user_has_purchased': user_has_purchased,
        'user_certified':user_certified
    }
    return render(request, template_name, context)


def course_list(request):
    email = request.session.get('Email')
    courses=Course.objects.all()
    return render (request,'courses.html',{'courses':courses, 'email': email})

def mcq(request,module_id):
    email = request.session.get('Email')
    user  = get_object_or_404(Userregister, email=email)
     
    request.session['module_id'] = module_id
    module =get_object_or_404(Module,id=module_id)

    # course
    course = module.course

    # all module
    modules = course.module_set.all()

    lesson= module.lesson_set.first()
    mcqs=lesson.mcqs.all()
    if not mcqs:
        mcqs=""


    if request.method == 'POST':
        lesson_id = request.POST.get('lesson_id')
        lesson    = get_object_or_404(Lesson, id=lesson_id)
        mcqs      = lesson.mcqs.all()
        total   = mcqs.count()
        correct = 0
        for q in mcqs:
            ans = request.POST.get(f'question_{q.id}')
            print(ans)
            if ans and ans == q.correct_option:
                print(ans==q.correct_option)
                correct += 1
        crs = lesson.module.course
        email = request.session.get('Email')
        user  = get_object_or_404(Userregister, email=email)
        LessonTestResult.objects.update_or_create(
            user   = user,
            lesson = lesson,
            course = crs,
            defaults = {'score': correct}
        )

        messages.success(request, f"You scored {correct} out of {total} on “{lesson.title}.”")
        return redirect('module_detail', module_id=module.id)
    print(mcqs)

    return render(request,'mcq.html',{'module':module,'lesson':lesson,'mcqs':mcqs, 'modules':modules, 'course':course,'user':user})


def module_detail(request,module_id):
    # user
    email = request.session.get('Email')
    user  = get_object_or_404(Userregister, email=email)
     
    # module
    request.session['module_id'] = module_id
    module =get_object_or_404(Module,id=module_id)
 
    course = module.course
    modules = course.module_set.all()
    lesson= module.lesson_set.first()
    if lesson.mcqs.all():
        mcqs=lesson.mcqs.all()
    else:
        mcqs=""
    
    user_certified =  modules.count() == LessonTestResult.objects.filter(user=user, course=course).count()

    if request.method == 'POST':
        lesson_id = request.POST.get('lesson_id')
        lesson  = get_object_or_404(Lesson, id=lesson_id)
        mcqs  = lesson.mcqs.all()
        total  = mcqs.count()
        correct = 0
        for q in mcqs:
            ans = request.POST.get(f'question_{q.id}')
            print(ans)
            if ans and ans == q.correct_option:
                print(ans==q.correct_option)
                correct += 1
        crs = lesson.module.course
        email = request.session.get('Email')
        user  = get_object_or_404(Userregister, email=email)
        LessonTestResult.objects.update_or_create(
            user   = user,
            lesson = lesson,
            course = crs,
            defaults = {'score': correct}
        )

        messages.success(request, f"You scored {correct} out of {total} on “{lesson.title}.”")
        return redirect('module_detail', module_id=module.id)
    # print(mcqs)

    return render(request,'modules_detail.html',{'module':module,'lesson':lesson,'mcqs':mcqs, 'modules':modules, 'user_certified':user_certified, 'course':course,'user':user})


def payment_success(request,course_id):
    course=get_object_or_404(Course,id=course_id)
    user_email = request.session.get('Email')
    if not user_email:
     return render(request,'login.html')
    
    user =get_object_or_404(Userregister,email=user_email)
    user.purchase_courses.add(course)
    
    return render(request,"payment_success.html",{"course":course})


def payment_failed(request):
    return render(request,'payment_failed.html')

def thanks(request):
    return render(request,'thanks.html')


def index(request):
    email = request.session.get('Email')
    if Userregister.objects.filter(email=email).exists():
        user  = Userregister.objects.filter(email=email).first()
    else:
        user = False
        email = False
    courses = Course.objects.all()[:9]
    return render(request, 'index.html', { 'email': email, 'courses':courses,'user':user})


def courses(request):
    courses=Course.objects.all()
    return render (request,'courses.html',{'courses':courses})


def  create_checkout_session(request,course_id):
    if not request.session.get('Email'):
        return redirect('login')
    
    course=Course.objects.get(id=course_id)
    if MCQQuestion.objects.filter(lesson__module__course__id=course_id).exists():


        session =stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items =[{
            'price_data':{
                'currency':'inr',
                'product_data':{
                    'name':course.title,
                },
                'unit_amount':int(course.price*100),
            },
            'quantity':1,
        }],
        mode='payment',
        success_url=f"https://technolearn.onrender.com/payment_success/{course_id}",
        cancel_url = f"https://technolearn.onrender.com/payment_failed/",
    )
        return redirect(session.url)
    else:
        return render(request, "under_progress.html")




def pdftext(request,lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        html_content = lesson.pdf_material  

        page_size  = request.POST.get('page_size', 'A4').upper()
        orientation = request.POST.get('orientation', 'P').upper() 
        font_size  = int(request.POST.get('font_size', '16'))

        buffer = BytesIO()
        pdf = FPDF(orientation=orientation, unit='mm', format=page_size)
        pdf.add_page()
        pdf.set_font("Helvetica", size=font_size)

        pdf.write_html(html_content)

        pdf.output(buffer)
        buffer.seek(0)

        response = HttpResponse(buffer.read(), content_type='application/pdf')
        filename = f"lesson_{lesson_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return render(request, 'download_notes.html')



def ask_openai(message):
    prompt=message
    client = genai.Client(api_key="AIzaSyAfEvQeUI7SzyaSNh74DjHxEUxYmUHgDKY")
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents='give anser in one line to this prompt : '+prompt)
    print(response.text) 
    return response.text



def chatbot(request):
    if not request.session.get('Email'):
        messages.success(request, "Please login first to start chat with your Personal AI.")
        return redirect('login')
    email = request.session.get('Email')
    user  = get_object_or_404(Userregister, email=email)
    chats = Chat.objects.filter(user=user).order_by('created_at')
    # chats = Chat.objects.filter(user_id = user.id)
    if request.method == 'POST':
        message  = request.POST.get('message', '').strip()
        response = ask_openai(message)
        Chat.objects.create(user = user, message  = message,response = response)      
        chat = Chat(user_id =user.id , message=message, response=response, created_at=timezone.now)
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats,'user': user})



def download_audio(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    text=lesson.pdf_material
    content = re.sub(r"<[^>]+>","", text)
    content=' '.join(content.split())
    return render(request,"download_audio.html", {'content':content})


def download_notes(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    text=lesson.pdf_material
    content = re.sub(r"<[^>]+>","", text)
    content=' '.join(content.split())
    return render(request,"download_notes.html", {'lesson':lesson, 'content':content})


def my_certificates(request):
    print("here1")
    if request.session.get('Email'):
        email = request.session.get('Email')
        user  = get_object_or_404(Userregister, email=email)
    else:
        return redirect('login')
    # courses = user.purchase_courses.all()
    print("here")
    certificates = UserCertificate.objects.filter(user=user).all()
    print(certificates)
    return render(request, "profile_certi.html", {'certificates': certificates})


def profile_section(request):
    email = request.session.get('Email')
    user  = get_object_or_404(Userregister, email=email)
    try:
        user_profile = Userregister.objects.get(id=user.id) 
    except Userregister.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        if user_profile:
            user_profile.name = name
            user_profile.email = email
            user_profile.save()
            request.session['Email'] = email

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_section') 
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'profile_section.html', context)


def generate_random_password(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))




def forgot_password(request):

    if request.method == 'POST' and request.POST.get('email'):
        email = request.POST['email'].strip()
        source = 'form'
    elif request.session.get('Email'):
        email = request.session['Email']
        source = 'session'
    else:
        return redirect('login')

    user = get_object_or_404(Userregister, email=email)

    # Generate password
    new_pass = generate_random_password(6)
    user.password = new_pass
    user.save()

    # mail new password
    send_mail(
        subject='Your New Password',
        message=(
            f'Hello {user.name},\n\n'
            f'Your password has been reset (via {source}).\n'
            f'Your new password is:\n\n'
            f'    {new_pass}\n\n'
            'Please log in and change it as soon as possible.\n\n'
            '— The TechnoLearn Team'
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return render(request, "send_password.html", {"user":user})

def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        email = request.session.get('Email')
        user  = get_object_or_404(Userregister, email=email)
        if  user.password != old_password:
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile_section')

        user.password = new_password
        user.save()
    
        messages.success(request, 'Password changed successfully.')
        return redirect('profile_section')  

    return render(request, 'profile_section.html')


def profile_course(request):
    email = request.session.get('Email')
    user  = get_object_or_404(Userregister, email=email)
    courses = user.purchase_courses.all()
    print(courses.count())

    course_data = []
    for course in courses:
        
        total_modules =  course.module_set.all().count() 
        user_certified = total_modules == LessonTestResult.objects.filter(user_id=user.id, course_id=course.id).count()

        course_data.append({
            'course': course,
            'total_modules': total_modules,
            'user_certified': user_certified,
        })

    context = {
        'course_data': course_data,
    }
    return render(request, 'profile_course.html', context)



@csrf_exempt
def generate_audio(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)

        # Parse incoming JSON data
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        rate = data.get('rate', 1.0) 

        if not text:
            return JsonResponse({'error': 'No text provided.'}, status=400)

        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        # Prepare response as downloadable MP3
        response = HttpResponse(mp3_buffer.read(), content_type='audio/mpeg')
        response['Content-Disposition'] = 'attachment; filename="speech.mp3"'
        return response

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def download_certificate(request, course_id):
    email  = request.session.get('Email')
    user   = get_object_or_404(Userregister, email=email)
    course = get_object_or_404(Course, id=course_id)

    try:
        cert = UserCertificate.objects.get(user=user, course=course)
        if cert.pdf_files:
            return FileResponse(
                cert.pdf_files,
                as_attachment=True,
                filename=f"{cert.name}_certificate.pdf"
            )
    except UserCertificate.DoesNotExist:
        cert = None

    buffer = BytesIO()
    PAGE_WIDTH, PAGE_HEIGHT = 2000, 1414
    p = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    tpl = os.path.join(settings.BASE_DIR, 'static', 'images', 'certify.png')
    p.drawImage(ImageReader(tpl), 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT)

    fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    pdfmetrics.registerFont(TTFont('Cinzel',         os.path.join(fonts_dir, 'Cinzel-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Cinzel-Bold',    os.path.join(fonts_dir, 'Cinzel-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSerif-Bold', os.path.join(fonts_dir, 'NotoSerif-Bold.ttf')))


    p.setFont('Cinzel', 71.4)
    p.setFillColor('#d1aa1e')
    p.drawCentredString(PAGE_WIDTH / 2 + 170, 698, user.name)

    p.setFont('NotoSerif-Bold', 46)
    p.setFillColor('#378a4d')
    p.drawCentredString(PAGE_WIDTH / 2 + 173, 563 , course.title)

    date_str = timezone.now().date().strftime('%d/%m/%Y')
    p.setFont('NotoSerif-Bold', 35)
    p.drawCentredString(830, 220, date_str)
    p.drawCentredString(1654, 220, course.instructor)

    p.showPage()
    p.save()
    buffer.seek(0)

    pdf_content = ContentFile(buffer.read())
    filename    = f"{user.name}_certificate.pdf"
    if not cert:
        cert = UserCertificate.objects.create(
            user=user,
            course=course,
            name=user.name,
            date_of_completion=timezone.now().date()
        )
    cert.pdf_files.save(filename, pdf_content)
    cert.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')



def about_us(request):
    if request.session.get('Email'):
        email = request.session.get('Email')
        user_login  = get_object_or_404(Userregister, email=email)
    else:
        user_login = False
    return render(request,'about.html', {'user_login':user_login})





def contact(request):
    print("post")
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        send_mail(
            subject=f"Thanks for contacting us, {name}!",
            message=(
                f"Hi {name},\n\n"
                f"We’ve received your message on “{subject}”.\n\n"
                f"Your message:\n{message}\n\n"
                "We’ll be in touch soon!\n\n"
                "— The TechnoLearn Team"
            ),
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('thanks')

    return render(request, "contact.html")

def logout_view(request):
    request.session.pop('Email', None)
    return redirect('index')
