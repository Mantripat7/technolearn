# myapp/context_processors.py

from .models import Course

def fcourse(request):
    """
    Adds a variable `all_courses` to every template context,
    containing Course.objects.all().
    """
    return {
        'fcourse': Course.objects.all()[:5]
    }
