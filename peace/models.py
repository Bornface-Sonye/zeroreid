from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
    
    
class County(models.Model):
    county_id = models.AutoField(primary_key=True)
    county_name = models.CharField(max_length=255, unique=True, help_text="Enter a valid County Name")

    def __str__(self):
        return self.county_name

class Constituency(models.Model):
    constituency_id = models.AutoField(primary_key=True)
    county_id = models.ForeignKey(County, on_delete=models.CASCADE)
    constituency_name = models.CharField(max_length=255, unique=True, help_text="Enter a valid Constituency Name")

    def __str__(self):
        return self.constituency_name

class Ward(models.Model):
    ward_id = models.AutoField(primary_key=True)
    constituency_id = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    ward_name = models.CharField(max_length=255, unique=True, help_text="Enter a valid Ward Name")

    def __str__(self):
        return self.ward_name

    
    
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    ward_id = models.ForeignKey(Ward, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=255, unique=True, help_text="Enter a valid Location Name")

    def __str__(self):
        return self.location_name
    
    
class Sub_Location(models.Model):
    sub_location_id = models.AutoField(primary_key=True)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    sub_location_name = models.CharField(max_length=255, unique=True, help_text="Enter a valid Sub Location Name")

    def __str__(self):
        return self.sub_location_name
    
    
class Police_Station(models.Model):
    police_station_id = models.AutoField(primary_key=True)
    police_station_name = models.CharField(max_length=255, unique=True, help_text="Enter a Police Station Name")
    sub_location_id = models.ForeignKey(Sub_Location, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.police_station_name
    
class Badge_Number(models.Model):
    badge_number_id = models.AutoField(primary_key=True)
    badge_number = models.CharField(max_length=255, unique=True, help_text="Enter a valid Badge Number")
    first_name = models.CharField(max_length=200, help_text="Enter a valid first name")
    last_name = models.CharField(max_length=200, help_text="Enter a valid last name")
    police_station_id = models.ForeignKey(Police_Station, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.badge_number
    
    

class Police_Officer(models.Model):
    badge_number = models.CharField(primary_key=True, max_length=255, unique=True, help_text="Enter a valid Badge Number")
    email_address = models.EmailField(max_length=200, unique=True, help_text="Enter a valid email address")
    password_hash = models.CharField(max_length=128, help_text="Enter a valid password")  # Store hashed password

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def clean(self):
        # Custom validation for password field
        if len(self.password_hash) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

    def __str__(self):
        return self.badge_number
    

class Suspect(models.Model):
    national_id_no = models.CharField(primary_key=True, max_length=20, unique=True, help_text="Enter a Suspect National ID No")
    suspect_name = models.CharField(max_length=255, default=" ", help_text="Enter Full Suspect Name")
    gender = models.CharField(max_length=10, help_text="Enter Suspect Gender")
    age = models.IntegerField(help_text="Enter Suspect Age")
    
    def __str__(self):
        return self.national_id_no
 

    
class Case(models.Model):
    ob_number = models.CharField(primary_key=True, max_length=255, unique=True, help_text="Enter OB Number")
    case_description = models.CharField(max_length=255, unique=True, help_text="Enter Case Description")
    badge_number = models.ForeignKey(Police_Officer, on_delete=models.CASCADE)
    national_id_no = models.ForeignKey(Suspect, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.ob_number
    



class Response(models.Model):
    response_id = models.AutoField(primary_key=True, help_text="Enter a valid testification id")
    ob_number = models.ForeignKey(Case, on_delete=models.CASCADE, help_text="Enter a valid OB Number")
    national_id_no = models.ForeignKey(Suspect, on_delete=models.CASCADE, help_text="Enter a valid Suspect Identifier")
    serial_number = models.CharField(max_length=200, unique=True, help_text="Auto-generated serial number", blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True, help_text="Date of submission", blank=True)
    trace = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], help_text="Any strong Trace of Suspect in Crime Scene?")
    recidivist = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], help_text="Involved in similar case?")
    question1 = models.CharField(max_length=250, default="", help_text="Can you describe what happened on the incident day providing as many details as possible")
    question2 = models.CharField(max_length=250, default="", help_text="Can you think of any reason why someone would lie about this incident ? If yes, explain.")
    question3 = models.CharField(max_length=250, default="", help_text="Are you aware of any other complaints made by the accuser ? If yes, State.")
    query1 = models.CharField(max_length=250, default="", help_text="Provide detailed description of the incident day's events.")
    query2 = models.CharField(max_length=250, default="", help_text="Any motive for dishonesty about the incident? Please elaborate if applicable.")
    query3 = models.CharField(max_length=250, default="", help_text="Have you heard of any additional complaints filed by the accuser? If so, specify.")
    
    
    
    def __str__(self):
        return f"{self.national_id_no}"
    
    
# models.py

class PasswordResetToken(models.Model):
    username = models.ForeignKey(Police_Officer,default=" ", on_delete=models.CASCADE)
    token = models.CharField(max_length=32, default=" ",)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.username}"


