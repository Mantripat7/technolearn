from django.db import models
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Course(models.Model):
    title= models.CharField(max_length=200)
    description=models.TextField()
    prerequisites=models.TextField(blank=True,null=True)
    instructor=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    image=models.ImageField(upload_to='course_images/',blank=True,null=True)
    pdf_material=models.FileField(upload_to='course_pdfs/',blank=True,null=True)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)

    def __str__(self):
        return f"{self.id}-{self.title}"
    
class Module(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    module=models.ForeignKey(Module,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    # content=RichTextUploadingField()
    video_url=models.URLField(blank=True,null=True)
    pdf_material = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class MCQQuestion(models.Model):
    lesson=models.ForeignKey("Lesson",on_delete=models.CASCADE,related_name="mcqs")
    question_text=models.TextField(max_length=255)
    option_a=models.CharField(max_length=255)
    option_b=models.CharField(max_length=255)
    option_c=models.CharField(max_length=255)
    option_d=models.CharField(max_length=255)
    correct_option=models.CharField(max_length=255)
    explanation=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.question_text
    
class Userregister(models.Model):
    name=models.CharField(max_length=1000)
    email=models.EmailField(max_length=1000)
    password=models.CharField(max_length=1000)
    purchase_courses=models.ManyToManyField(Course,blank=True)

    def __str__(self):
        return self.name
    

class Chat(models.Model):
    user = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name}: {self.message}'

class person(models.Model):
    first_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)



class LessonTestResult(models.Model):
    user = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='test_results')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='test_results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson_test_results')  # New field
    score = models.IntegerField(help_text="Raw count of correct answers")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.name} - {self.lesson.title}: {self.score}"
    

    
class UserCertificate(models.Model):
    user = models.ForeignKey(Userregister, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # User's name for the cert
    date_of_completion = models.DateField(auto_now_add=True)
    pdf_files = models.FileField(upload_to='certificates/', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.name} - {self.course.title}"
    

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
  
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
