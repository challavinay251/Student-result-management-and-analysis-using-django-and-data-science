from django.shortcuts import render
from app.forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import openpyxl
from app.forms import ExcelFileForm
import io
from .forms import EnrollmentForm
from django.shortcuts import render, HttpResponse
from .models import ExcelFile
from .forms import AnalysisForm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def index(request):
    return render(request,'app/index.html')
@login_required
def special(request):
    return HttpResponse("You are logged in !")
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        #profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() :
            user = user_form.save()
            user.set_password(user.password)
            user.save()
        else:
            print(user_form.errors,)
    else:
        user_form = UserForm()
        # profile_form = UserProfileInfoForm()
    return render(request,'app/registration.html',
                          {'user_form':user_form,
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('profile')

            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'app/login.html', {})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user = request.user
    # Extract any additional information needed for the profile page
    context = {'user': user}
    return render(request, 'app/profile.html', context)

def home(request):
    return render(request,'app/home.html')

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.save(commit=False)
            wb = openpyxl.load_workbook(excel_file.file)
            # Process the data as needed
            excel_file.save()
            return render(request,'app/home.html')
    else:
        form = ExcelFileForm()
    return render(request, 'app/upload_excel.html', {'form': form})
'''
# def excel_data(request):
#     excel_file = ExcelFile.objects.get(pk='4') # replace 1 with the ID of the file you want to retrieve
#     file_data = excel_file.file.read()
#     df = pd.read_excel(io.BytesIO(file_data))
#     # do something with the data, like render it in a template or save it to the database
#     return render(request, 'APP/view_excel.html', {'data': df.to_html()})
 '''
# displaying student respones sheet using enrolment number
from .forms import ExcelDataForm
from django.shortcuts import render, HttpResponse
from .models import ExcelFile
def respones(request):
    if request.method == 'POST':
        form = ExcelDataForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            enrolment_number = form.cleaned_data['enrolment_number']
            try:
                excel_file = ExcelFile.objects.get(date=date)
            except ExcelFile.DoesNotExist:
                return HttpResponse('Error: No exam on the submitted date.')
            file_data = excel_file.file.read()
            df = pd.read_excel(io.BytesIO(file_data))
            df.rename(columns={'Enrolment number': 'enrolment_number'}, inplace=True)
            condition = df['enrolment_number'] == enrolment_number
            filtered_df = df[condition]
            if filtered_df.empty:
                return HttpResponse('Error: ABSENT or incorrect enrolment_number..')
            context = {'data': filtered_df}
            return render(request, 'app/respones.html', context)
    else:
        form = ExcelDataForm()
    return render(request, 'app/excel_form.html', {'form': form})

# fetching the data from all the file using enrolment_number
from .forms import EnrollmentForm
import pandas as pd
import io

def marksheet(request):
    file_ids = ExcelFile.objects.values_list('id', flat=True)
    form = EnrollmentForm(request.POST or None)
    data_list = []
    error_messages = []
    if form.is_valid():
        enrolment_number = form.cleaned_data['enrolment_number']
        matching_data_found = False
        for file_id in file_ids:
            excel_file = ExcelFile.objects.get(pk=file_id)
            file_data = excel_file.file.read()
            df = pd.read_excel(io.BytesIO(file_data))
            # Filter the DataFrame based on a condition
            df.rename(columns={'Enrolment number': 'enrolment_number'}, inplace=True)
            df.rename(columns={'Student Name': 'Student_Name'}, inplace=True)
            condition = df['enrolment_number'] == enrolment_number
            filtered_df = df[condition]
            if not filtered_df.empty:
                matching_data_found = True
                filtered_df['File_ID'] = excel_file.id  # Add 'File ID' column
                data_list.append(filtered_df)
            else:
                error_messages.append(f" {enrolment_number}  is absent on exam File ID: {file_id}")
        # Pass the form, list of filtered DataFrames, and error messages to the template as context data
        context = {'form': form, 'data_list': data_list, 'error_messages': error_messages, 'matching_data_found': matching_data_found}
        return render(request, 'app/marksheet.html', context)
    # If the form is not valid, render the template with the form only
    context = {'form': form}
    return render(request, 'app/marksheet_form.html', context)


# analysis part
def analyze_data(request):
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            enrolment_number = form.cleaned_data['enrolment_number']
            file_ids = ExcelFile.objects.values_list('id', flat=True)
            subjects = ['MATHS', 'PHY', 'CHE']
            marks_data = {subject: [] for subject in subjects}
            matching_files = []  # List to store matching files
            non_matching_files = []  # List to store non-matching files
            for file_id in file_ids:
                excel_file = ExcelFile.objects.get(pk=file_id)
                df = pd.read_excel(excel_file.file)
                df.rename(columns={'Enrolment number': 'enrolment_number'}, inplace=True)
                student_data = df[df['enrolment_number'] == enrolment_number]
                if student_data.empty:
                    non_matching_files.append(excel_file)
                    continue
                matching_files.append(excel_file)
                marks = student_data[subjects].values.tolist()[0]
                for i, subject in enumerate(subjects):
                    marks_data[subject].append(marks[i])
            plt.figure(figsize=(10, 6))
            x = np.arange(len(matching_files))
            width = 0.2
            for i, subject in enumerate(subjects):
                plt.bar(x + i * width, marks_data[subject], width, label=subject)
            plt.xlabel(' EXAM File ID')
            plt.ylabel('Marks')
            plt.title(f'{enrolment_number} - Performance in Maths, Physics, and Chemistry')
            plt.xticks(x, [file.id for file in matching_files])
            plt.legend()
            chart_file = 'static/images1/chart.png'
            plt.savefig(chart_file)
            plt.clf()
            context = {
                'chart_file': chart_file,
                'matching_files': matching_files,
                'non_matching_files': non_matching_files,
            }
            return render(request, 'APP/analysis_results.html', context)
    else:
        form = AnalysisForm()
    return render(request, 'APP/analysis_form.html', {'form': form})

# fetching the result using enrolment_number and exam date
# from .models import ExcelFile
# from .forms import ExcelDataForm
# from django.shortcuts import render, HttpResponse
def excel_data(request):
    if request.method == 'POST':
        form = ExcelDataForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            enrolment_number = form.cleaned_data['enrolment_number']
            try:
                excel_file = ExcelFile.objects.get(date=date)
            except ExcelFile.DoesNotExist:
                return HttpResponse('Error: No exam on the submitted date.')
            file_data = excel_file.file.read()
            df = pd.read_excel(io.BytesIO(file_data))
            # filter the DataFrame based on a condition
            df.rename(columns={'Enrolment number': 'enrolment_number'}, inplace=True)
            df.rename(columns={'Student Name': 'Student_Name'}, inplace=True)
            condition = df['enrolment_number'] == enrolment_number
            filtered_df = df[condition]
            if filtered_df.empty:
                return HttpResponse('Error: ABSENT or incorrect enrolment_number.')
            # pass the filtered_df to the template as context data
            context = {'data': filtered_df}
            return render(request, 'app/view_excel.html', context)
    else:
        form = ExcelDataForm()
    return render(request, 'app/excel_form.html', {'form': form})

#sending ranks to mails

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import ExcelFile
import pandas as pd
from django.http import HttpResponse

def send_rank_emails(request):
    # Retrieve the Excel file from the database
    excel_file = ExcelFile.objects.get(pk=9)  # Replace '1' with the appropriate file ID or query to retrieve the file
    # Read the Excel file data into a DataFrame
    df = pd.read_excel(excel_file.file)
    # Extract email addresses and other relevant data from the DataFrame
    recipients = df.to_dict('records')  # Assumes each row represents a recipient with relevant data
    # Set up the email server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Use the appropriate port for your SMTP server
    smtp_username = 'vinaychalla654@gmail.com'
    smtp_password = 'uortshmfgmvqmqpb'
    # Connect to the SMTP server and send emails
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        for recipient in recipients:
            email_address = recipient['Email Address']
            # Prepare the personalized email content
            subject = 'Rank Announcement'
            # Create the email body as a list of tables
            tables = []
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Enrolment number</th><th>Batch</th><th>DATE</th><th>SET</th></tr>')
            tables.append(f'<tr><td>{recipient["Enrolment number"]}</td><td>{recipient["Batch"]}</td><td>{recipient["Timestamp"]}</td><td>{recipient["SET"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            # Add another table here
            tables.append('<tr><th>MATHS</th><th>PHYSICS</th><th>CHEMISTRY</th><th>Total Marks</th><th>Rank</th></tr>')
            tables.append(f'<tr><td>{recipient["MATHS"]}</td><td>{recipient["PHY"]}</td><td>{recipient["CHE"]}</td><td>{recipient["TOTAL"]}</td><td>{recipient["RANK"]}</td></tr>')
            tables.append('</table>')
            # Add another table here
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>MATHS RANK</th><th>PHYSICS RANK</th><th>CHEMISTRY RANK</th></tr>')
            tables.append(f'<tr><td>{recipient["MATHS RANK"]}</td><td>{recipient["PHY RANK"]}</td><td>{recipient["CHE RANK"]}</td></tr>')
            tables.append('</table>')
            #tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<span><h1><center> STUDENT RESPONSE </center> </h1></span>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Q5</th><th>Q6</th><th>Q7</th><th>Q8</th><th>Q9</th><th>Q10</th></tr>')
            tables.append(f'<tr><td>{recipient["Q2"]}</td><td>{recipient["Q2"]}</td><td>{recipient["Q3"]}</td><td>{recipient["Q4"]}</td><td>{recipient["Q5"]}</td><td>{recipient["Q6"]}</td><td>{recipient["Q7"]}</td><td>{recipient["Q8"]}</td><td>{recipient["Q9"]}</td><td>{recipient["Q10"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q11</th><th>Q12</th><th>Q13</th><th>Q14</th><th>Q15</th><th>Q16</th><th>Q17</th><th>Q18</th><th>Q19</th><th>Q20</th></tr>')
            tables.append(f'<tr><td>{recipient["Q11"]}</td><td>{recipient["Q12"]}</td><td>{recipient["Q13"]}</td><td>{recipient["Q14"]}</td><td>{recipient["Q15"]}</td><td>{recipient["Q16"]}</td><td>{recipient["Q17"]}</td><td>{recipient["Q18"]}</td><td>{recipient["Q19"]}</td><td>{recipient["Q20"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q21</th><th>Q22</th><th>Q23</th><th>Q24</th><th>Q25</th><th>Q26</th><th>Q27</th><th>Q28</th><th>Q29</th><th>Q30</th></tr>')
            tables.append(f'<tr><td>{recipient["Q22"]}</td><td>{recipient["Q22"]}</td><td>{recipient["Q23"]}</td><td>{recipient["Q24"]}</td><td>{recipient["Q25"]}</td><td>{recipient["Q26"]}</td><td>{recipient["Q27"]}</td><td>{recipient["Q28"]}</td><td>{recipient["Q29"]}</td><td>{recipient["Q30"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q31</th><th>Q32</th><th>Q33</th><th>Q34</th><th>Q35</th><th>Q36</th><th>Q37</th><th>Q28</th><th>Q39</th><th>Q40</th></tr>')
            tables.append(f'<tr><td>{recipient["Q31"]}</td><td>{recipient["Q32"]}</td><td>{recipient["Q33"]}</td><td>{recipient["Q34"]}</td><td>{recipient["Q35"]}</td><td>{recipient["Q36"]}</td><td>{recipient["Q37"]}</td><td>{recipient["Q38"]}</td><td>{recipient["Q39"]}</td><td>{recipient["Q40"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q41</th><th>Q42</th><th>Q43</th><th>Q44</th><th>Q45</th><th>Q46</th><th>Q47</th><th>Q48</th><th>Q49</th><th>Q50</th></tr>')
            tables.append(f'<tr><td>{recipient["Q41"]}</td><td>{recipient["Q42"]}</td><td>{recipient["Q43"]}</td><td>{recipient["Q44"]}</td><td>{recipient["Q45"]}</td><td>{recipient["Q46"]}</td><td>{recipient["Q47"]}</td><td>{recipient["Q48"]}</td><td>{recipient["Q49"]}</td><td>{recipient["Q50"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q51</th><th>Q52</th><th>Q53</th><th>Q54</th><th>Q55</th><th>Q56</th><th>Q57</th><th>Q58</th><th>Q59</th><th>Q60</th></tr>')
            tables.append(f'<tr><td>{recipient["Q51"]}</td><td>{recipient["Q52"]}</td><td>{recipient["Q53"]}</td><td>{recipient["Q54"]}</td><td>{recipient["Q55"]}</td><td>{recipient["Q56"]}</td><td>{recipient["Q57"]}</td><td>{recipient["Q58"]}</td><td>{recipient["Q59"]}</td><td>{recipient["Q60"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q61</th><th>Q62</th><th>Q63</th><th>Q64</th><th>Q65</th><th>Q66</th><th>Q67</th><th>Q68</th><th>Q69</th><th>Q70</th></tr>')
            tables.append(f'<tr><td>{recipient["Q61"]}</td><td>{recipient["Q62"]}</td><td>{recipient["Q63"]}</td><td>{recipient["Q64"]}</td><td>{recipient["Q65"]}</td><td>{recipient["Q66"]}</td><td>{recipient["Q67"]}</td><td>{recipient["Q68"]}</td><td>{recipient["Q69"]}</td><td>{recipient["Q70"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q71</th><th>Q72</th><th>Q73</th><th>Q74</th><th>Q75</th><th>Q76</th><th>Q77</th><th>Q78</th><th>Q79</th><th>Q80</th></tr>')
            tables.append(f'<tr><td>{recipient["Q72"]}</td><td>{recipient["Q72"]}</td><td>{recipient["Q73"]}</td><td>{recipient["Q74"]}</td><td>{recipient["Q75"]}</td><td>{recipient["Q76"]}</td><td>{recipient["Q77"]}</td><td>{recipient["Q78"]}</td><td>{recipient["Q79"]}</td><td>{recipient["Q80"]}</td></tr>')
            tables.append('</table>')
            tables.append('<p style="margin-bottom: 20px;"></p>')
            tables.append('<table border="1" cellpadding="5" cellspacing="0">')
            tables.append('<tr><th>Q81</th><th>Q82</th><th>Q83</th><th>Q84</th><th>Q85</th><th>Q86</th><th>Q87</th><th>Q88</th><th>Q89</th><th>Q90</th></tr>')
            tables.append(f'<tr><td>{recipient["Q81"]}</td><td>{recipient["Q82"]}</td><td>{recipient["Q83"]}</td><td>{recipient["Q84"]}</td><td>{recipient["Q85"]}</td><td>{recipient["Q86"]}</td><td>{recipient["Q87"]}</td><td>{recipient["Q88"]}</td><td>{recipient["Q89"]}</td><td>{recipient["Q90"]}</td></tr>')
            tables.append('</table>')
            # Create the email message
            message = MIMEMultipart()
            message['From'] = 'vinaychalla654@gmail.com'
            message['To'] = email_address
            message['Subject'] = subject
            message.attach(MIMEText(''.join(tables), 'html'))
            # Send the email
            server.sendmail(smtp_username, email_address, message.as_string())

    return HttpResponse('Rank emails sent successfully')
