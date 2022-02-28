from datetime import datetime


def year(request):
    current_year = datetime.now().year
    return {
        'year': int(current_year),
    }
