import pandas as pd
from django.utils.timezone import now, timedelta

def generate_report(report_type, filters):
    from inventory.models import Chemical
    data = None
    if report_type == 'expiry':
        data = Chemical.objects.filter(expiry_date__lte=now()).values()
    elif report_type == 'inventory':
        date_range = filters.get('date_range', {})
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')

        if start_date and end_date:
            data = Chemical.objects.filter(last_used_range=[start_date, end_date]).values()
        elif filters.get('range_type') == 'day':
            data = Chemical.objects.filter(last_used_gte=now() - timedelta(days=1)).values()
        elif filters.get('range_type') == 'week':
            data = Chemical.objects.filter(last_used_gte=now() - timedelta(weeks=1)).values()
        elif filters.get('range_type') == 'month':
            data = Chemical.objects.filter(last_used_gte=now() - timedelta(dayss=30)).values()
        else:
            return None
    else:
        return None
    
    if not data.exists():
        return None
    
    df = pd.DataFrame(data)
    file_name = f'{report_type}_report_{now().strftime("%Y%m%d%H%M%S")}.xlsx'
    file_path = f'media/reports/{file_name}'
    df.to_excel(file_path, index=False)
    return file_path


