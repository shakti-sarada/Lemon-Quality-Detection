from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from PIL import Image
import numpy as np
import tensorflow as tf
import json
import os

# Create your views here.
def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def login(request):
    return render(request, "login.html")

# def register(request):
#     return render(request, "register.html")

# Load pre-trained model
model = tf.keras.models.load_model('E:\\Lemon Quality Detection\\lemonqualitydetection\\newlemon.h5',compile=False)

QUALITY_DETECTION_RESULTS = {
    0: "Bad",
    1: "Good",
    2: "Neutral",
}

def predict(request):
    if request.method == 'POST':
        image = request.FILES.get('image-input')
        if not image:
            return HttpResponse('No image uploaded', status=400)

        # Define directories for uploaded and preprocessed images
        upload_dir = 'uploads/'
        preprocess_dir = 'preprocessed/'

        # Create directories if they don't exist
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(preprocess_dir, exist_ok=True)

        # Save uploaded image in the upload directory
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        # Load and preprocess the image for prediction
        img = Image.open(upload_dir + filename)
        img = img.resize((224, 224))  # Resize the image to 224x224
        img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]

        # Save the preprocessed image in the preprocess directory
        preprocessed_filename = 'preprocessed_' + filename
        img.save(os.path.join(preprocess_dir, preprocessed_filename))

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction using the pre-trained model
        prediction = model.predict(img_array)
        prediction_class = np.argmax(prediction)
        quality_detection_result = QUALITY_DETECTION_RESULTS.get(prediction_class, "Image Not Detected")

        return HttpResponse(json.dumps({
            'uploaded_file_url': uploaded_file_url,
            'preprocessed_file_url': fs.url(preprocessed_filename),
            'quality_detection_result': quality_detection_result,
        }), content_type='application/json')

    return render(request, 'prediction.html')


from django.http import JsonResponse, HttpResponseBadRequest
import logging
import yagmail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email(request):
    if request.method == 'POST':
        try:
            # Get the form data
            name = request.POST.get('name')
            sender_email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if not name or not sender_email or not subject or not message:
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

            # Setup yagmail with credentials
            yag = yagmail.SMTP(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            # Send email
            yag.send(
                to='shaktisahoo65@gmail.com',  # Replace with your email
                subject=subject,
                contents=f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message}"
            )

            return JsonResponse({'status': 'success', 'message': 'Email sent successfully!'})
        
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)

    return HttpResponseBadRequest('Invalid request method')


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth import login, authenticate

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration was successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})







