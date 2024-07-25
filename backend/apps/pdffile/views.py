import base64
import json
import os
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa
from django.template.loader import get_template, render_to_string
from weasyprint import HTML


# Create your views here.


def save_base64_image(base64_str, file_path):
    image_data = base64.b64decode(base64_str)
    with open(file_path, 'wb') as f:
        f.write(image_data)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    print(template)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


@csrf_exempt
def generate_pdf(request):
    # Example context with placeholders and base64 encoded signature image
    context = {
        'name': 'John Doe',
        'date': '2024-07-18',
    }

    # Handle the signature
    signature_base64 = request.POST.get('signature')
    if signature_base64:

        signature_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
        print(signature_path)
        save_base64_image(signature_base64, signature_path)
        context['signature'] = signature_path

    pdf = render_to_pdf('confiscation-template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)


@csrf_exempt
def render_pdf_view(request):
    context = {
        'name': 'John Doe',
        'date': '2024-07-18',
    }

    event_json = json.loads(request.POST.get('events', ""))
    if event_json:
        context['events'] = event_json

    # Handle the signature
    signature_base64 = request.POST.get('signature')
    if signature_base64:
        signature_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
        save_base64_image(signature_base64, signature_path)
        context['signature'] = signature_base64

    html_string = render_to_string('confiscation-template.html', context)
    html = HTML(string=html_string)
    print(html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report.pdf"'
    html.write_pdf(response)
    return response
