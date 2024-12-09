from django.views import View
from .models import Suspect, Case,Response, Badge_Number,Police_Station
from .models import County, PasswordResetToken, Constituency,Ward,Location,Sub_Location,Police_Officer
from .forms import PasswordResetForm, InterrogatorReportForm, ResetForm, AnswerForm, LoginForm, SignUpForm




import hashlib
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import logout as django_logout
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from tabulate import tabulate
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph



import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
import joblib
import os
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy as sp


class SignUpView(View):
    template_name = 'signup.html'

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)

        if form.is_valid():
            badge_number=form.cleaned_data['badge_number']
            email_address = form.cleaned_data['email_address']
            password_hash = form.cleaned_data['password_hash']

            # REQ-1: Check if account already exists
            if Police_Officer.objects.filter(email_address=email_address).exists():
                form.add_error(None, "This email address has already been used!")
                return render(request, self.template_name, {'form': form})
            else:
                # Create the account
                # Save the application
                new_account = form.save(commit=False)
                new_account.set_password(form.cleaned_data['password_hash'])
                new_account.save()
                return redirect('login')
        else:
            # If the form is not valid, render the template with the form and errors
            return render(request, self.template_name, {'form': form})



class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data['email_address']
            password = form.cleaned_data['password']
            police = Police_Officer.objects.filter(email_address=email_address).first()
            if police and police.check_password(password):
                # Authentication successful
                request.session['email_address'] = police.email_address
                police_email = police.email_address
                return redirect('dashboard')
            else:
                # Authentication failed
                error_message = 'Invalid email or password'
                return render(request, self.template_name, {'form': form, 'error_message': error_message})
        else:
            error_message = 'Invalid email or password'
            return render(request, self.template_name, {'form': form, 'error_message': error_message})





class ErrorPageView(View):
    def get(self,request):
        return render(request, 'interrogator_error.html')  
      
class SuccessPageView(View):
    def get(self, request, *args, **kwargs):
        serial_number = self.kwargs.get('serial_number', None)
        return render(request, 'interrogator_success.html', {'serial_number': serial_number})

class HomePageView(View):
    def get(self,request):
        return render(request, 'index.html')    
    


def logout(request):
    if request.method == 'POST':
        django_logout(request)
        return redirect('home')  # Redirect to home page after logout
    return render(request, 'dashboard.html')


def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data['email_address']
            email_address = Police_Officer.objects.filter(email_address=email_address).first()
            if email_address:
                try:
                    # Generate a unique token
                    token = get_random_string(length=32)
                    # Save the token to the database
                    PasswordResetToken.objects.create(username=email_address, token=token)
                    # Send password reset email
                    reset_link = request.build_absolute_uri('/') + f'reset-password/{token}'
                    send_mail(
                        'Reset Your Password',
                        f'Click the link to reset your password: {reset_link}',
                        settings.EMAIL_HOST_USER,
                        [email_address],
                        fail_silently=False,
                    )
                    # Redirect to a success page or show a message
                    return redirect('password_reset_done')
                except Exception as e:
                    # Handle any exception gracefully
                    error_message = f"An error occurred: {str(e)}"
                    return render(request, 'reset_password.html', {'form': form, 'error_message': error_message})
            else:
                # Display error message for non-existing email
                error_message = "Email Address does not exist in our records."
                return render(request, 'reset_password.html', {'form': form, 'error_message': error_message})
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', {'form': form})

def reset_password_confirm(request, token):
    # Check if the token exists in the database
    password_reset_token = PasswordResetToken.objects.filter(token=token).first()
    if password_reset_token:
        if request.method == 'POST':
            # Update the user's password
            form = ResetForm(request.POST)
            if form.is_valid():
                badge_number=form.cleaned_data['badge_number']
                email_address = form.cleaned_data['email_address']
                password_hash = form.cleaned_data['password_hash']
                police = get_object_or_404(PoliceOfficer, badge_number=badge_number)
                police.delete()
                police = form.save(commit=False)
                police.set_password(form.cleaned_data['password_hash'])
                police.save()
                # Delete the used token
                password_reset_token.delete()
                return redirect('login')
            else:
                form = ResetForm()
            return render(request, 'reset_password_confirm.html', {'form': form, 'token': token})
    else:
        # Token is invalid or expired, handle appropriately
        return render(request, 'reset_password_token_invalid.html')



def generate_serial_number(national_id_no, ob_number):
    data_string = f"{national_id_no}-{ob_number}"
    unique_identifier = str(uuid.uuid4())
    combined_string = f"{data_string}-{unique_identifier}"
    serial_number = hashlib.md5(combined_string.encode()).hexdigest()
    truncated_hash = serial_number[:8]
    return truncated_hash


class DashboardView(View):
    template_name = 'dashboard.html'
    
    def get(self, request):
        answer_form = AnswerForm()
        report_form = InterrogatorReportForm()
        return render(request, self.template_name, {'answer_form': answer_form, 'report_form': report_form})

    def post(self, request):
        answer_form = AnswerForm(request.POST)
        report_form = InterrogatorReportForm(request.POST)
         

        if answer_form.is_valid():
            ob_number = answer_form.cleaned_data['ob_number']
            national_id_no = answer_form.cleaned_data['national_id_no']
            trace = answer_form.cleaned_data['trace']
            recidivist = answer_form.cleaned_data['recidivist']
            question1 = answer_form.cleaned_data['question1']
            question2 = answer_form.cleaned_data['question2']
            question3 = answer_form.cleaned_data['question3']
            query1 = answer_form.cleaned_data['query1']
            query2 = answer_form.cleaned_data['query2']
            query3 = answer_form.cleaned_data['query3']
            
            
            # Check if the Case OB Number exists in the Case Table
            if not Case.objects.filter(ob_number=ob_number).exists():
                answer_form.add_error(None, "Invalid Case OB Number.")
                return render(request, self.template_name, {'answer_form': answer_form})
            
            
            
            # Check if the Suspect ID NO. exists in the Suspect Table
            if not Suspect.objects.filter(national_id_no=national_id_no).exists():
                answer_form.add_error(None, "Invalid Suspect National Identification Number.")
                return render(request, self.template_name, {'answer_form': answer_form})
            
            
            
            # Check for existing response
            if Response.objects.filter(ob_number=ob_number, national_id_no=national_id_no).exists():
                answer_form.add_error(None, "Intorragation Information for This Suspect ID and Case OB Number already submitted, sorry.")
                return render(request, self.template_name, {'answer_form': answer_form})

            
            serial_number = generate_serial_number(national_id_no, ob_number)
            response = answer_form.save(commit=False)
            response.serial_number = serial_number
            response.save()

            return redirect('success', serial_number=serial_number)
        
        elif report_form.is_valid():
            serial_number = report_form.cleaned_data['serial_number']
            try:
                response = get_object_or_404(Response, serial_number=serial_number)
                suspect = response.national_id_no
                national_id_no = suspect
                suspect_data = get_object_or_404(Suspect, national_id_no=national_id_no)
                ob_number = response.ob_number
                case_data = get_object_or_404(Case, ob_number=ob_number)
                
                
                
                ''' if not Response.objects.filter(serial_number=serial_number).exists():
                    report_form.add_error(None, "Case Information for the Provided Serial Number does not exist, sorry.")
                    return render(request, self.template_name, {'report_form': report_form}) '''               
            except Response.DoesNotExist:
                return render(request, 'interrogator_error.html', {'error_message': f'Suspect Report with serial number "{serial_number}" not found.'})
        
        
        
            # My processing for generating report data
            mlm = MachineLearningModel()
            accuracy = mlm.accuracy()
            sentiment_analyser = SentimentAnalyzer()
            criminal = CriminalPrediction()
            national_id_no = suspect.national_id_no
            suspect_name = suspect_data.suspect_name
            age = suspect_data.age
            gender = suspect_data.gender
            ob_number = response.ob_number
            case_description = case_data.case_description
            badge_number = case_data.badge_number
            recidivist = response.recidivist
            firstResponse = response.trace
            question1 = response.question1
            question2 = response.question2
            question3 = response.question3
            query1 = response.query1
            query2 = response.query2
            query3 = response.query3
            
            text_groups = {
                'firstSet': (question1, query1),
                'secondSet': (question2, query2),
                'thirdSet': (question3, query3),
            }
            
            consistency_score = sentiment_analyser.calculate_consistency_score(text_groups)
            trace = response.trace
            honesty_score = sentiment_analyser.is_honest(text_groups)
            criminal.data_retrieval(suspect_name, age, recidivist, trace, honesty_score, consistency_score, gender)
            #criminal.data_preparation()
            result = criminal.data_preparation()
            
            
            report_data = {
                'ob_number': ob_number,
                'case_description':case_description,
                'badge_number': badge_number,
                'national_id_no': national_id_no,
                'name': suspect_name,
                'age':age,
                'gender':gender,
                'recidivist':recidivist,
                'trace':trace,
                'honesty_score':honesty_score,
                'consistency_score':consistency_score,
                'submission_date': response.date_recorded,
                'serial_number': serial_number,
                'result': result,
                'accuracy': accuracy,
            }
            
            
            # Generate PDF
            pdf_bytes = generate_pdf(report_data)
               
            # Return the PDF file as a response
            #response = HttpResponse(pdf_bytes, content_type='interrogator/pdf')
            #response['Content-Disposition'] = f'attachment; filename="{suspect_name}_report.pdf"'
            
            # Return the PDF file as a response
            # Trigger the download of the PDF file
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{suspect_name}_report.pdf"'
            
            
            # Add a custom response header to trigger JavaScript to stop the progress animation
            response['X-Stop-Progress'] = 'true'
            return response
            
            
            # If neither form is valid or processed, return the template with both forms       
        return render(request, self.template_name, {'answer_form': answer_form, 'report_form': report_form})


def generate_pdf(report_data):
    buffer = BytesIO()
    pdf_canvas = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Set font and size
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    style_normal.fontName = 'Helvetica'
    style_heading.fontName = 'Helvetica'
    style_normal.fontSize = 12
    style_heading.fontSize = 14

    # Define additional information to include at the top
    additional_info = [
        "PEACE 2017 REFORMED, THE PEACE DIGITAL",
        "P.O. BOX. 197-40400 SARE-AWENDO",
        "Email: bornfacesonye@gmail.com",
        
        "TEL: +254-798073204",
        "DEPARTMENT:KAMITI",
        "CASE YEAR: 2024",
        "_____________________________________ \n\n",
    ]

    # Create a paragraph for additional information
    additional_info_paragraphs = [Paragraph(info, style_normal) for info in additional_info]

    # Calculate the height of the additional information
    additional_info_height = sum(paragraph.wrapOn(pdf_canvas, pdf_canvas.width, pdf_canvas.height)[1] for paragraph in additional_info_paragraphs)

    # Define table data
    table_data = [
        ["Case Information"],
        ["Case OB Number:", report_data['ob_number']],
        ["Case Description:", report_data['case_description']],
        ["Officer In_Charge:", report_data['badge_number']],
        ["Suspect National Identification No:", report_data['national_id_no']],
        ["Suspect Name:", report_data['name']],
        ["Suspect Age:", report_data['age']],
        ["Suspect Gender:", report_data['gender']],
        ["Have The Suspect been in Similar Case Before:", report_data['recidivist']],
        ["Any Trace of Suspect in Crime Scene:", report_data['trace']],
        ["Is The Suspect Honest:", report_data['honesty_score']],
        ["Suspect Consistency Score:", report_data['consistency_score']],
        ["Response Submission Date:", report_data['submission_date']],
        ["Accuracy of the Model Used:", report_data['accuracy']],
        ["Prediction Data:", report_data['result']],
        
    ]

    # Calculate the required height for the table
    table_height = len(table_data) * style_normal.fontSize

    # Adjust the page height based on the content
    pdf_canvas.pagesize = landscape(letter)
    pdf_canvas.height = max(additional_info_height, table_height) + inch  # Add some extra space between content and table

    # Create a table for main data
    main_table = Table(table_data, colWidths=[4*inch, 4*inch])  # Adjusting column widths

    # Set table style for main data
    style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # Header background color
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),  # Content background color
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 12),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('SPAN', (0, 0), (1, 0)),  # Merge cells for the heading
                        ])

    main_table.setStyle(style)

    # Add page border
    frame_styling = TableStyle([('BOX', (0, 0), (-1, -1), 2, colors.black)])
    main_table.setStyle(frame_styling)

    # Add tables to the PDF
    elements = additional_info_paragraphs + [Spacer(1, 0.25 * inch), main_table]

    # Build PDF
    pdf_canvas.build(elements)

    # Save the PDF file
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize SentimentAnalyzer with NLTK Sentiment Intensity Analyzer and spaCy NLP model.
        """
        self.sid = nltk.sentiment.SentimentIntensityAnalyzer()
        self.nlp = sp.load("en_core_web_sm")

    def is_honest(self, text_group: dict) -> str:
        
        """
        Determine honesty based on sentiment score.
        
        Parameters:
            text (str): Input text to analyze.
        
        Returns:
            str: 'Y' if sentiment score is >=50, 'N' otherwise.
        """     
        honesty_scores = []
        for key, (text1, text2) in text_group.items():
            try:
                doc1 = self.nlp(text1)
                doc2 = self.nlp(text2)
                similarity = doc1.similarity(doc2)
                honesty_scores.append(similarity)
                
            except Exception as e:
                
                return 'No'
            
        average_score = sum(honesty_scores) / len(honesty_scores) if honesty_scores else 0
        honesty_score = round(average_score * 100)
                
        if honesty_score >= 50:
             return 'Yes' # Obedient
        else:
             return 'No' # Not obedient

    def calculate_consistency_score(self, text_groups: dict) -> int:
        """
        Calculate consistency score based on multiple pairs of texts.
        
        Parameters:
            text_groups (dict): Dictionary where the keys represent group names
                and the values are tuples containing two texts.
        
        Returns:
            int: Average consistency score rounded to the nearest integer.
        """
        consistency_scores = []
        for key, (text1, text2) in text_groups.items():
            try:
                doc1 = self.nlp(text1)
                doc2 = self.nlp(text2)
                similarity = doc1.similarity(doc2)
                consistency_scores.append(similarity)
            except Exception as e:
                # Return a default value if an error occurs during consistency score calculation
                return 0
        
        average_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
        return round(average_consistency * 100)

class MachineLearningModel:
    def __init__(self):
        self.new_data = None
        self.prediction = None
        self.numeric_feature = None
        self.categorical_feature = None
        self.training_features = None
        self.predictions = None
        self.model = None
        self.scaler = None
        self.actual_labels = None
        self.file_path = os.path.join(settings.BASE_DIR, 'peace', 'peace', 'crime.csv')
        self.df = pd.read_csv(self.file_path)
        self.feature_names = ['Age','Recidivist','Trace','Honest','ConsistencyScore','Gender']
        self.training_features = self.df[self.feature_names]
        self.outcome_name = ['Criminal']
        self.outcome_labels = self.df[self.outcome_name]
        self.numeric_feature_names = ['Age','ConsistencyScore']
        self.categorical_feature_names = ['Recidivist','Trace','Honest','Gender']
        ss = StandardScaler()
        ss.fit(self.training_features[self.numeric_feature_names])
        self.training_features[self.numeric_feature_names] = ss.transform(self.training_features[self.numeric_feature_names])
        self.training_features = pd.get_dummies(self.training_features,columns=self.categorical_feature_names)
        self.categorical_engineered_features = list(set(self.training_features.columns)-set(self.numeric_feature_names))
        self.lr = LogisticRegression()
        self.model = self.lr.fit(self.training_features,np.array(self.outcome_labels['Criminal']))
        self.pred_labels = self.model.predict(self.training_features)
        self.actual_labels = np.array(self.outcome_labels['Criminal'])
        if not os.path.exists('Model'):
            os.mkdir('Model')
        if not os.path.exists('Scaler'):
            os.mkdir('Scaler')
        joblib.dump(self.model,r'Model/model.pickle')
        joblib.dump(ss,r'Scaler/scaler.pickle')
        self.model = joblib.load(r'Model/model.pickle')
        self.scaler = joblib.load(r'Scaler/scaler.pickle')

    def accuracy(self):
        acc = accuracy_score(self.actual_labels, self.pred_labels)
        class_stats = classification_report(self.actual_labels, self.pred_labels)
        accuracy_row = f"{acc * 100:.2f}%"
        class_stats_row = "Classification Stats:\n" + class_stats

        return accuracy_row

class CriminalPrediction:
    def __init__(self):
        self.new_data = None
        self.prediction = None
        self.training_features = None
        self.numeric_feature = None
        self.categorical_feature = None
        self.model = joblib.load(r'Model/model.pickle')
        self.scaler = joblib.load(r'Scaler/scaler.pickle')
        self.prediction = None
        self.predictions = None
        self.file_path = os.path.join(settings.BASE_DIR, 'peace', 'peace', 'crime.csv')
        self.df = pd.read_csv(self.file_path)
        self.feature_names = ['Age','Recidivist','Trace','Honest','ConsistencyScore','Gender']
        self.training_features = self.df[self.feature_names]
        self.outcome_name = ['Criminal']
        self.outcome_labels =self.df[self.outcome_name]
        self.numeric_feature_names = ['Age','ConsistencyScore']
        self.categorical_feature_names = ['Recidivist', 'Trace','Honest','Gender']
        self.ss = StandardScaler()
        self.ss.fit(self.training_features[self.numeric_feature_names])
        self.training_features[self.numeric_feature_names] = self.ss.transform(self.training_features[self.numeric_feature_names])
        self.training_features = pd.get_dummies(self.training_features,columns=self.categorical_feature_names)
        
    def data_retrieval(self,name,age,recidivist,trace,honest,consistency_score,gender):
        self.new_data = pd.DataFrame([{'Name': name,
                        'Age': age,
                        'Recidivist': recidivist,
                        'Trace': trace,
                        'Honest': honest,
                        'ConsistencyScore': consistency_score,
                        'Gender': gender
                        }])
    
    def data_preparation(self):
        self.prediction = self.new_data.copy()
        self.numeric_feature = ['Age','ConsistencyScore']
        self.categorical_feature = ['Recidivist_Yes','Recidivist_No','Trace_Yes','Trace_No','Honest_Yes','Honest_No','Gender_Male','Gender_Female']
        self.prediction[self.numeric_feature] = self.scaler.transform(self.prediction[self.numeric_feature])
        self.prediction= pd.get_dummies(self.prediction,columns=['Recidivist', 'Trace','Honest','Gender'])
        for feature in self.categorical_feature:
            if feature not in self.prediction.columns:
                self.prediction[feature] = 0 #Add missing categorical feature columns with 0 columns
        self.prediction = self.prediction[self.training_features.columns]
        self.predictions = self.model.predict(self.prediction)
        self.new_data['Criminal'] = self.predictions
        result = self.new_data[self.outcome_name][self.new_data['Criminal'] != 0].to_string(index=False)
        return result    
       


