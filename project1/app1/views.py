
from django.shortcuts import render, redirect
from .forms import LoginForm, ExpenseForm
from .models import User
from .models import Expense

import boto3
from django.http import JsonResponse

import csv
import tempfile
from django.conf import settings

from botocore.exceptions import ClientError
from botocore.exceptions import ClientError
from django.http import HttpResponse


# if we not put the detail insetting.py then we use this code


#-------------for data upload to s3 bucket--------------
# def upload_to_s3(request):
#     # Explicitly specify AWS credentials

#     aws_region = 'us-east-1'

#     try:
#         # Create S3 client with explicit credentials
#         s3 = boto3.client('s3', 
#                            aws_access_key_id=aws_access_key_id, 
#                            aws_secret_access_key=aws_secret_access_key, 
#                            region_name=aws_region)

#         # Example data to upload (replace this with your actual data)
#         expenses = Expense.objects.all()

#         # Example bucket name (replace this with your actual bucket name)
#         bucket_name = 'sharing-data-flats'

#         # Create a temporary file to store the CSV data
#         with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
#             csv_writer = csv.writer(temp_file)
#             for expense in expenses:
#                 csv_writer.writerow([expense.amount,expense.payee,expense.payer])

#         # Upload data to S3
#         with open(temp_file.name, 'rb') as file:
#             s3.put_object(Bucket=bucket_name, Key='expenses.csv', Body=file)
        
#         return JsonResponse({'success': True})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


#----------------------

# from setting.py we are getting key and credetional
#---upload to s3 bucket-----
def upload_to_s3(request):
    # Explicitly specify AWS credentials
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    aws_region = settings.AWS_REGION
    bucket_name = settings.AWS_S3_BUCKET_NAME

    try:
        # Create S3 client with explicit credentials
        s3 = boto3.client('s3', 
                           aws_access_key_id=aws_access_key_id, 
                           aws_secret_access_key=aws_secret_access_key, 
                           region_name=aws_region)

        # Example data to upload (replace this with your actual data)
        expenses = Expense.objects.all()

        # Create a temporary file to store the CSV data
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            csv_writer = csv.writer(temp_file)
            for expense in expenses:
                csv_writer.writerow([expense.amount,expense.payee,expense.payer])

        # Upload data to S3
        with open(temp_file.name, 'rb') as file:
            s3.put_object(Bucket=bucket_name, Key='expenses.csv', Body=file)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




#download from s3
def download_from_s3(request):
    try:
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        aws_region = settings.AWS_REGION
        bucket_name = settings.AWS_S3_BUCKET_NAME

        # Replace 'file_key' with the key of the file you want to download from S3
        file_key = 'expenses.csv'

        # Create S3 client with explicit credentials
        s3 = boto3.client('s3', 
                          aws_access_key_id=aws_access_key_id, 
                          aws_secret_access_key=aws_secret_access_key, 
                          region_name=aws_region)

        # Fetch the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)

        # Prepare HTTP response with file data
        file_data = response['Body'].read()
        response = HttpResponse(file_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_key}"'
        return response
    except ClientError as e:
        return HttpResponse(f"S3 Error: {e.response['Error']['Code']}", status=500)
    except Exception as e:
        return HttpResponse(str(e), status=500)





#deleet from s3
def delete_from_s3(request):
    try:
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        aws_region = settings.AWS_REGION
        bucket_name = settings.AWS_S3_BUCKET_NAME

        # Replace 'file_key' with the key of the file you want to delete from S3
        file_key = 'expenses.csv'

        # Create S3 client with explicit credentials
        s3 = boto3.client('s3', 
                          aws_access_key_id=aws_access_key_id, 
                          aws_secret_access_key=aws_secret_access_key, 
                          region_name=aws_region)

        # Delete the file from S3
        s3.delete_object(Bucket=bucket_name, Key=file_key)

        return JsonResponse({'success': True})
    except ClientError as e:
        return JsonResponse({'success': False, 'error': f"S3 Error: {e.response['Error']['Code']}"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




#for login
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Check if the user exists in the database
            # request.session['user_id'] = user.id
            return redirect('add_expense',username=username)
            # try:
            #     user = User.objects.get(username=username, password=password)
            #     return render(request, 'loggedin.html', {'username': username})
            # except User.DoesNotExist:
            #     return render(request, 'login.html',{'form': 'error_message'})
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})






# for expense calculate
def add_expense(request, username):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            share_type = form.cleaned_data.get('share_type')
            selected_users = form.cleaned_data.get('users')

            if share_type == 'equally':
                amount_per_user = amount / len(selected_users)
                for user in selected_users:
                    if user.username != username:
                        # Check if there is an existing expense between the same payer and payee
                        existing_expense = Expense.objects.filter(payer=username,payee=user.username)
                        # print("12",existing_expense)

                        print("Existing expenses between", username, "and", user.username)
                        for expense in existing_expense:
                            print(expense)

                        if existing_expense:
                            existing_expense_instance = existing_expense.first()
                            existing_expense_instance.amount -= amount_per_user
                            existing_expense_instance.save()
                        else:
                            # existing_expense = Expense.objects.filter(payer=user.username, payee=username).first()
                            Expense.objects.create(payer=user.username, amount=amount_per_user, payee=username)
                            # Expense.objects.create(payer=username, amount=-amount_per_user, payee=user.username)
            elif share_type == 'percentage':
                total_percentage = sum(map(float, request.POST.getlist('percentage')))
                if total_percentage != 100:
                    return render(request, 'add_expense.html', {'form': form, 'username': username, 'error_message': 'Total percentage must be 100.'})
                for user, percentage in zip(selected_users, request.POST.getlist('percentage')):
                    if user.username != username:
                        # Check if there is an existing expense between the same payer and payee
                        existing_expense = Expense.objects.filter(payer=user.username, payee=username).first()
                        if existing_expense:
                            existing_expense.amount += (amount * float(percentage)) / 100
                            existing_expense.save()
                        else:
                            amount_for_user = (amount * float(percentage)) / 100
                            Expense.objects.create(payer=user.username, amount=amount_for_user, payee=username)
                            Expense.objects.create(payer=username, amount=-amount_for_user, payee=user.username)
            # elif share_type == 'Exactly':
            #     print('"Hello')
            #     for user, exact_amount in zip(selected_users, request.POST.getlist('exact_amount')):
            #         if user.username != username:
            #             # Check if there is an existing expense between the same payer and payee
            #             existing_expense = Expense.objects.filter(payer=user.username, payee=username).first()
            #             if existing_expense:
            #                 existing_expense.amount += float(exact_amount)
            #                 existing_expense.save()
            #             else:
            #                 Expense.objects.create(payer=user.username, amount=float(exact_amount), payee=username)


            elif share_type == 'exactly':
                # If the share type is 'Exactly', process the amount fields
                for user in form.cleaned_data['users']:
                    amount_field_name = f'amount_{user.id}'
                    amount = form.cleaned_data.get(amount_field_name)
                    # Here you can do whatever you want with the amount data,
                    # such as saving it to the database or performing calculations
                    print(f"Amount for user {user.username}: {amount}")
            # If the form is valid, you can save the expense or perform any other required actions
            # For demonstration purposes, I'll redirect back to the same page for now
            


            else:
                # Process other sharing types
                pass
                
         
            return redirect('expense_added')
    else:
        form = ExpenseForm(initial={'username': username})
    return render(request, 'add_expense.html', {'form': form, 'username': username})



#data show here
def expense_added(request):
    user=Expense.objects.all()
    return render(request, 'expense_added.html',{'data':user})