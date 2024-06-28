from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import JsonResponse
from .models import User,CustomerOrder,CustomerData,TemplateActualNormal,CustomerOrderForecast,TemplateSpecial, StockData
from django.template import loader
from django.shortcuts import get_object_or_404
from django.http import Http404
import pandas as pd
from django.core.files.storage import default_storage
import os
import csv
from .forms import FileUploadForm
import json
from datetime import datetime, timedelta
from dateutil import parser
from collections import defaultdict
import holidays
import math
from django.db import transaction
from django.db.models import Max


# Create your views here.
def index(request):
    return render(request,'index.html')

def login_form_view(request):
    return render(request, 'login.html')

def signup_form_view(request):
    return render(request, 'signup.html')

def master_data_view(request):
    return render(request, "master.html")

def customer_order_view(request):
    return render(request, "customer.html")

def templates_view(request):
    return render(request,'templates.html')

def delete_template(request, template_id):
    if request.method == 'DELETE':
        try:
            # Retrieve all rows with the specified templateID
            templates = TemplateActualNormal.objects.filter(templateID=template_id)
        except TemplateActualNormal.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Template not found'})

        # Delete all rows
        templates.delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def update_template(request, template_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        try:
            templates = TemplateActualNormal.objects.filter(templateID=template_id)
        except TemplateActualNormal.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Template not found'})

        column_names = data.get('columnNames', [])
        column_numbers = data.get('columnNumbers', [])

        if len(column_names) != len(column_numbers):
            return JsonResponse({'status': 'error', 'message': 'Column names and numbers lists must have the same length'})

        # Loop through each template in the queryset and update its fields
        for i, template in enumerate(templates):
            template.templateID = data.get('templateID', template.templateID)
            template.templateName = data.get('templateName', template.templateName)
            template.templateType = data.get('templateType', template.templateType)
            template.startRow = data.get('rowStarted', template.startRow)
            template.columnName = column_names[i] if i < len(column_names) else template.columnName
            template.columnNumber = column_numbers[i] if i < len(column_numbers) else template.columnNumber
            template.fileType = data.get('fileType', template.fileType)
            template.condition = data.get('condition', template.condition)
            template.amountdaysplus = data.get('amountdaysplus', template.amountdaysplus)
            template.columnNumberplus = data.get('columnNumberplus', template.columnNumberplus)
            template.needBackupData = data.get('needBackupData', template.needBackupData)

            template.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 

def signup_user(request):
    if request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            password = request.POST['password']
            department = request.POST['department']

            #new_user = User(fname =fname , lname=lname, email=email, password=password, department=department)
            new_user = User(fname=fname, lname=lname, email=email, password=password, department=department)
            new_user.save()
            print("User Successfully Created!")
            return redirect('index')
    
def login_user(request):
     if request.method == 'POST':
          email = request.POST['email']
          password = request.POST['password']
          print(email)
          print(password)

          user = authenticate(request, email=email, password=password)

          if user is not None:
               login(request,user)
               print("User logged in successfully!")
               return redirect('index')
          else:
               print(user)
               print("Invalid email or password. Please try again.")
               return redirect('login')
     return render(request, 'login.html')

import json
from django.http import JsonResponse

def normal_template(request):
    if request.method == 'POST':
        try:
            '''latest_template = TemplateActualNormal.objects.order_by('-templateID').first()
            if latest_template:
                next_template_id = latest_template.templateID + 1
            else:
                next_template_id = 1'''
            with transaction.atomic():
                latest_normal_template = TemplateActualNormal.objects.order_by('-templateID').first()
                latest_special_template = TemplateSpecial.objects.order_by('-templateID').first()
                
                if latest_normal_template and latest_special_template:
                    next_template_id = max(latest_normal_template.templateID, latest_special_template.templateID) + 1
                elif latest_normal_template:
                    next_template_id = latest_normal_template.templateID + 1
                elif latest_special_template:
                    next_template_id = latest_special_template.templateID + 1
                else:
                    next_template_id = 1

            data = json.loads(request.body)
            templateName = data.get('templateName')
            templateType = data.get('templateType')
            rowStarted = data.get('rowStarted')
            columnNames = data.get('columnNames')
            columnNumbers = data.get('columnNumbers')
            fileType = data.get('fileType')
            condition = data.get('condition')
            needBackupData = data.get('needBackupData')
            amountdaysplus = data.get('amountdaysplus', 0)  # Default to 0 if not provided
            columnNumberplus = data.get('columnNumberplus', 0)  # Default to 0 if not provided

           # Zip column names and numbers into a list of dictionaries
            columns = [dict(zip(columnNames, columnNumbers))]

            # Iterate over the list of dictionaries and create TemplateActualNormal instances
            for item in columns:
                for name, number in item.items():
                    new_normal_template = TemplateActualNormal(
                        templateID=next_template_id,
                        templateName=templateName,
                        templateType=templateType,
                        startRow=rowStarted,
                        fileType=fileType,
                        columnName=name,
                        columnNumber=number,
                        condition=condition,
                        needBackupData=needBackupData,
                        amountdaysplus=amountdaysplus,
                        columnNumberplus=columnNumberplus
                    )
                    new_normal_template.save()
            
            print("New normal template(s) successfully created")
            return redirect('templates')  # Assuming 'templates' is the name of the URL pattern you want to redirect to
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
     
def get_normal_templates(request):
    # Retrieve all TemplateActualNormal instances from the database
    templates = TemplateActualNormal.objects.all()

    # Serialize the templates data into JSON
    serialized_templates = []
    for template in templates:
        serialized_templates.append({
            'templateID': template.templateID,
            'templateName': template.templateName,
            'templateType': template.templateType,
            'startRow': template.startRow,
            'fileType': template.fileType,
            'condition': template.condition,
            'columnName': template.columnName,
            'columnNumber' : template.columnNumber,
            'amountdaysplus' : template.amountdaysplus,
            'columnNumberplus' : template.columnNumberplus,
            'needBackupData' : template.needBackupData,
        })
    
    # Return the serialized templates data as JSON response
    return JsonResponse(serialized_templates, safe=False)
    

def importOrder_form(request):
    return render(request,'importOrder.html')

def get_all_template_names_IDs(request):
    templates = TemplateActualNormal.objects.all()
    special_templates = TemplateSpecial.objects.all()

    template_names_ID = {}
    for template in templates:
        template_names_ID[template.templateID] = template.templateName
    for sp_template in special_templates:
        template_names_ID[sp_template.templateID] = sp_template.templateName

    return JsonResponse(template_names_ID, safe=False)

def count_holidays(month, year, country='TH'):
    holiday_list = holidays.CountryHoliday(country, years=int(year))
    count = sum(1 for date in holiday_list if date.month == int(month))
    return count

def count_holidays(month, year, country):
    # Dummy function to return the number of holidays in a given month and year
    # Replace with actual logic for counting holidays
    return 2  # Example: Assume there are 2 holidays

def is_weekend(date):
    # Check if the given date is a weekend (Saturday=5, Sunday=6)
    return date.weekday() >= 5
    
def handle_template_and_file(request): 
    if request.method == 'POST':
        if 'file' in request.FILES:
            # Upload the file
            uploaded_file = request.FILES['file']
            #save_path = 'D:/Freya/production_control_project/pc_project_env/the_project/media_files' 
            save_path = 'C:/inetpub/wwwroot/production-line-project/pc_project_env - Copy/the_project/media_files' 
            file_path = os.path.join(save_path, uploaded_file.name)
            default_storage.save(file_path, uploaded_file)
            
            # Get the template name from the request
            templateSelect = request.POST.get('templateSelect')
            templateType = request.POST.get('templateType')
            startDate = request.POST.get('startDate')
            print("templateSelect ",templateSelect)
            print("templateType ",templateType)
            print("startDate ",startDate)

            try:
                print("inside try ")
                columns_to_read = []
                # Retrieve template information from the database

                #--------------------For Normal Templates----------------------#
                templates = TemplateActualNormal.objects.filter(templateID = templateSelect)
                '''if not templates:
                    raise Http404("Template does not exist")'''
                if templates:

                    serialized_templates = []
                    current_template = None
                    for template in templates:
                        if current_template is None or template.templateID != current_template['templateID']:
                            if current_template is not None:
                                serialized_templates.append(current_template)
                            current_template = {
                                'templateID': template.templateID,
                                'templateName': template.templateName,
                                'startRow': template.startRow,
                                'fileType': template.fileType,
                                'templateType': template.templateType,
                                'condition': template.condition,
                                'needBackupData': template.needBackupData,
                                'amountdaysplus': template.amountdaysplus,
                                'columnNumberplus': template.columnNumberplus,
                                'columnDetails': []
                            }
                        current_template['columnDetails'].append({
                            'columnName': template.columnName,
                            'columnNumber': template.columnNumber,
                        })
                    print("current_template: ",current_template)

                    if current_template is not None:
                        serialized_templates.append(current_template)  

                    start = end = 0
                    for number in current_template['columnDetails']:
                        if  number['columnNumber'] != "0" or number['columnNumber'] != 0:
                            if "," in number['columnNumber']:
                                start, end = number['columnNumber'].split(',')
                                print("start != end ",start != end)
                                if start == end:  #same start and end
                                    columns_to_read.append(int(start))
                                else:
                                    print("Not same")
                                    print("start: ",start)
                                    print("end: ",end)
                                    #will do some logic if start and end not same
                                    start = int(start)
                                    end = int(end)
                                    for i in range(start, end + 1):  # Include end value
                                        columns_to_read.append(int(i))
                                    print("columns_to_read here ", columns_to_read)
                            else:
                                if number['columnNumber'] != '0' or number['columnNumber'] != "0": #summarize orders when start date and end
                                    print("inside this condition")
                                    columns_to_read.append(int(number['columnNumber']))

                                    the_condition = current_template['condition']
                                    print("the_condition insdie this condition ")
                                #print("or directly to this")
                        
                    columns_to_read = sorted(columns_to_read, reverse=False)
                    columns_to_read = [col for col in columns_to_read if col != 0]         

                    print("columns_to_read first ", columns_to_read)

                    start_row = current_template['startRow']
                    print("start_row ",start_row)

                    fileType = current_template['fileType']
                    columnDetails = current_template['columnDetails']
                    customerCode = int(columnDetails[0]['columnNumber'])
                    customerPartNumber = int(columnDetails[1]['columnNumber'])
                    print("customerPartNumber: ",customerPartNumber)
                    print("fileType",fileType)
                    if (fileType == "csv"):
                        data = pd.read_csv(file_path, header=None, usecols=columns_to_read, skiprows=start_row)
                    elif(fileType == "txt"):
                        data = pd.read_csv(file_path, sep='|', header=None, usecols=columns_to_read, skiprows=start_row)
                    elif(fileType == "xls" or fileType == "xlsx"):
                        data = pd.read_excel(file_path, usecols=columns_to_read, skiprows=start_row)
                    else:
                        print("Unsupported file type")                    
                    print("data ",data)

                    # Drop rows where customerPartNumber column contains NaN
                    data.dropna(subset=[customerPartNumber], inplace=True)

                    if templateType == "actual-FA": #for actual-forecast template
                        print("For acutal-FA")
                        
                        the_condition = current_template['condition']
                        print("condition has to use is ", the_condition)

                        dic = {}
                        new_data = pd.DataFrame(data) 
                        for i, column in enumerate(columns_to_read):
                            # Get the column data
                            col = new_data.iloc[:, i]
                            print("col is ", col)
                            print("column ",column)

                            for k, j in col.items():
                                if isinstance(j, str):  # Ensure the item is a string before processing
                                    # Remove any =' or " characters
                                    if '="' in j or '"' in j:
                                        j = j.replace('="', '').replace('"', '')

                                    # Remove leading zero from any purely numeric string
                                    print(j, "j.isdigit? ",j.isdigit())
                                    if j.isdigit():
                                        j = str(int(j))

                                    new_data.iloc[k, i] = j

                            dic[column] = new_data.iloc[:, i]

                        print("dic", dic)
                        df = pd.DataFrame(dic) 
                        print("df is ",df)

                        startOrderQty = 0
                        endOrderQty = 0
                        orderQty = columnDetails[2]['columnNumber']
                        if "," in orderQty:
                            orderQty = orderQty.split(',')
                        if orderQty[0] == orderQty[1]:
                            startOrderQty = endOrderQty = orderQty = int(orderQty[0])
                        elif orderQty[0] != orderQty[1]:
                            startOrderQty = int(orderQty[0])
                            endOrderQty = int(orderQty[1])
                        
                        startdeliveryDate = enddeliveryDate = 0
                        deliveryDate = columnDetails[3]['columnNumber']
                        if "," in deliveryDate:
                            deliveryDate = deliveryDate.split(',')
                        if deliveryDate[0] == deliveryDate[1]:
                            startdeliveryDate = enddeliveryDate = deliveryDate = int(deliveryDate[0])
                        elif deliveryDate[0] != deliveryDate[1]:
                            startdeliveryDate= int(deliveryDate[0])
                            enddeliveryDate = int(deliveryDate[1])
                            if enddeliveryDate - startdeliveryDate <= 3:
                                concatenated_column = ""
                                for column_number in range(startdeliveryDate, enddeliveryDate + 1):
                                    for each_row in df[column_number]:
                                        if isinstance(each_row, int) and each_row < 10:
                                            each_row = "0" + str(each_row)
                                    concatenated_column += df[column_number].astype(str).str.zfill(2)
                                # Assign concatenated column to a new column
                                colName = str(startdeliveryDate) + "," +str(enddeliveryDate)
                                df[colName] = concatenated_column

                                for column_number in range(startdeliveryDate, enddeliveryDate + 1):
                                    df = df.drop(column_number, axis=1)

                                print("df after concatenated \n",df)
                                return JsonResponse({'template': serialized_templates, 'data': df.to_dict(), 'result': df.to_dict()})
                            else:
                                print("chnage columns to rows")


                        deliveryTime = int(columnDetails[4]['columnNumber'])
                        deliveryPlant = int(columnDetails[5]['columnNumber'])

                        if the_condition.startswith("Summarize"): #summarize order quantity if they have the same date and group by customer part number
                            
                            aggregate_functions = {
                                orderQty : "sum", #Order qty when it's only one column
                                customerCode : "first", #Customer code
                                customerPartNumber : "first", #Customer part number
                            }
                            df_new = df.groupby(deliveryDate) #Delivery Date when it's only one column
                            # Group by deliveryDate first, then by customerPartNumber
                            #df_new = df.groupby([deliveryDate, customerPartNumber])
                            df_new = df.groupby(deliveryDate)
                            result = df_new.agg(aggregate_functions)
                            result.reset_index(inplace=True)
                            print(result)
                            return JsonResponse({'template': serialized_templates, 'data': data.to_dict(), 'result': result.to_dict()})

                        elif the_condition.startswith("Need"): #needs to add days to the delivery date column
                            # Assuming df is your DataFrame and columns_to_read is your list of columns
                            for i, column in enumerate(columns_to_read):
                                if column == current_template['columnNumberplus']:
                                    print("columns_to_read[i] == current_template['columnNumberplus']:", column == current_template['columnNumberplus'])
                                    
                                    # Extract the date strings from the DataFrame column
                                    date_strings = df.iloc[:, i]
                                    
                                    for key, date_string in date_strings.items():
                                        print(date_string)
                                        try:
                                            # Parse the date string using dateutil.parser
                                            date = parser.parse(str(date_string))
                                            print(date)

                                            # Add the specified number of days to the date
                                            new_date = date + timedelta(days=current_template['amountdaysplus'])

                                            # Format the new date back to the original format (YYYYMMDD for consistency)
                                            df.iloc[key, i] = new_date.strftime("%Y%m%d")
                                            print("new date_string[key]", df.iloc[key, i])
                                        except (ValueError, OverflowError) as e:
                                            print(f"Error parsing date string {date_string}: {e}")

                                dic[column] = df.iloc[:, i]
                            # Create DataFrame with all rows
                            result = pd.DataFrame(dic)
                            return JsonResponse({'template': serialized_templates, 'data': data.to_dict(), 'result': result.to_dict()})
                        

                        return JsonResponse({'template': serialized_templates, 'data': data.to_dict(), 'result': df.to_dict()})
                    
                    if templateType == "forecast-only":
                        print("columns_to_read ", columns_to_read)
                        print("For forecast-only")
                        print("startDate have to use is ", startDate) # 2024-05-01
                        start_date = datetime.strptime(startDate, "%Y-%m-%d")
                        start_year = start_date.strftime("%Y")
                        start_month = start_date.strftime("%m")
                        print("start month ", start_month)
                        print("start year ", start_year)

                        columnDetails = current_template['columnDetails']
                        customerCode = int(columnDetails[0]['columnNumber'])
                        customerPartNumber = int(columnDetails[1]['columnNumber'])

                        startOrderQty = 0
                        endOrderQty = 0
                        orderQty = columnDetails[2]['columnNumber']
                        deli_date_list = []
                        order_qty_list = []

                        startdeliveryDate = enddeliveryDate = 0
                        deliveryDate = columnDetails[3]['columnNumber']
                        if "," in deliveryDate:
                            deliveryDate = deliveryDate.split(',')
                        if deliveryDate[0] == deliveryDate[1]:
                            startdeliveryDate = enddeliveryDate = deliveryDate = int(deliveryDate[0])
                            deliveryDateStr = str(startdeliveryDate) 
                        elif deliveryDate[0] != deliveryDate[1]:
                            startdeliveryDate= int(deliveryDate[0])
                            enddeliveryDate = int(deliveryDate[1])
                            deliveryDateStr = str(startdeliveryDate) + ","+ str(enddeliveryDate)

                        if "," in orderQty:
                            orderQty = orderQty.split(',')
                        if orderQty[0] == orderQty[1]:
                            startOrderQty = endOrderQty = orderQty = int(orderQty[0])
                            orderQtyStr = str(startOrderQty)
                        elif orderQty[0] != orderQty[1]:
                            startOrderQty = int(orderQty[0])
                            endOrderQty = int(orderQty[1])
                            orderQtyStr = str(startOrderQty) + ","+ str(endOrderQty)
                            if int(endOrderQty - startOrderQty) <= 2:  # when they have two months total forecast
                                no_of_days = 0
                                if int(start_month) in (1, 3, 5, 7, 8, 10, 12):
                                    no_of_days = 31
                                elif int(start_month) in (4, 6, 9, 11):
                                    no_of_days = 30
                                else:
                                    no_of_days = 29

                                N = start_month
                                NY = start_year
                                country = 'TH'
                                start_month = start_date.strftime("%m")
                                print("start_month ",start_month)
                                forecast_startDate_str = str(start_year) + str(start_month).zfill(2) + "01"
                                forecast_startDate = datetime.strptime(forecast_startDate_str, "%Y%m%d")

                                print("forecast_startDate:", forecast_startDate_str)

                                forecast_endDate = (forecast_startDate + timedelta(days=30))  # Approximate two-month span

                                # Generate all days within the date range
                                all_days = pd.date_range(start=forecast_startDate, end=forecast_endDate)

                                # Filter out weekends (Saturday and Sunday) to get only working days
                                working_days = [day for day in all_days if day.weekday() < 5]
                                total_working_days = len(working_days)

                                print("Working days:", working_days)
                                print("Total working days:", total_working_days)                       

                                for column_number in [startOrderQty, endOrderQty]:  # Columns containing quantities
                                    for each_row in data[column_number]:
                                        each_dayQty = math.ceil(each_row / total_working_days)
                                        day_counter = 0

                                        '''for _ in range(1):  # Repeat for two months
                                            # Update forecast start date
                                            start_month = int(start_month)+1
                                            if start_month > 12:
                                                start_year = int(start_year) + 1
                                                start_month = 1'''
                                        
                                        #start_month_str = str(start_month).zfill(2)
                                        #print("start_month_str inside ",start_month_str)
                                        forecast_startDate_str = str(start_year) + str(start_month) + "01"
                                        print("forecast_startDate_str ", forecast_startDate_str)
                                        forecast_startDate = datetime.strptime(forecast_startDate_str, "%Y%m%d")
                                        print("forecast_startDate ", forecast_startDate)
                                        
                                        
                                        # Recalculate working days
                                        forecast_endDate = (forecast_startDate + timedelta(days=29))
                                        all_days = pd.date_range(start=forecast_startDate, end=forecast_endDate)
                                        working_days = [day for day in all_days if day.weekday() < 5]
                                        
                                        for i, current_date in enumerate(working_days):
                                            if day_counter < total_working_days:
                                                deli_date_list.append(current_date.strftime("%Y%m%d"))
                                                order_qty_list.append(each_dayQty)
                                                day_counter += 1
                                        
                                        if int(start_month) <= int(N):
                                            start_month = int(start_month)+1
                                            if start_month > 12:
                                                start_year = int(start_year) + 1
                                                start_month = 1
                                        else:
                                            start_month = N


                                # Flatten the data to match deli_date_list and order_qty_list
                                flattened_data = []
                                for col in range(startOrderQty, endOrderQty + 1):
                                    for each_row in data[col]:
                                        flattened_data.append(each_row)
                                
                                print("flattened_data ",flattened_data)


                                new_data = pd.DataFrame(data)
                                print("new_data is\n", new_data)
                                print("order_qty_list ",order_qty_list)
                                print("len of order_qty_list ", len(order_qty_list))
                                print("deli_date_list ", deli_date_list)
                                print("len of deli_date_list ", len(deli_date_list))

                                # Duplicate each row of new_data for the length of deli_date_list
                                #expanded_data = new_data.loc[new_data.index.repeat(len(deli_date_list)//4)].reset_index(drop=True)
                                #expanded_data = new_data.loc[new_data.index.repeat(len(deli_date_list) // len(new_data))].reset_index(drop=True)

                                # Calculate the number of repetitions needed to match the lengths of deli_date_list and order_qty_list
                                num_repetitions = math.ceil(len(deli_date_list) / len(new_data))

                                # Repeat rows of new_data based on the calculated number of repetitions
                                expanded_data = new_data.loc[new_data.index.repeat(num_repetitions)].reset_index(drop=True)

                                # Truncate expanded_data to match the length of deli_date_list
                                expanded_data = expanded_data.iloc[:len(deli_date_list)]
                                print("expanded_data is\n", expanded_data)

                                if startOrderQty in expanded_data.columns:
                                    expanded_data.drop(columns=[startOrderQty], inplace=True)

                                if endOrderQty in expanded_data.columns:
                                    expanded_data.drop(columns=[endOrderQty], inplace=True)
                                
                                print("expanded_data after drop\n", expanded_data)

                                # Add new columns
                                expanded_data[deliveryDateStr] = deli_date_list
                                expanded_data[orderQtyStr] = order_qty_list

                                print("expanded_data is\n", expanded_data)

                                #new_data['deli_date'] = deli_date_list
                                #new_data['order_qty'] = order_qty_list

                                #print("new_data is\n", new_data)
                                return JsonResponse({'template': serialized_templates, 'data': expanded_data.to_dict(), 'result': expanded_data.to_dict()})

                        orderQtyStr = str(startOrderQty) + ","+ str(endOrderQty)
                        
                        startdeliveryDate = enddeliveryDate = 0
                        deliveryDate = columnDetails[3]['columnNumber']
                        if "," in deliveryDate:
                            deliveryDate = deliveryDate.split(',')
                        if deliveryDate[0] == deliveryDate[1]:
                            startdeliveryDate = enddeliveryDate = deliveryDate = int(deliveryDate[0])
                            deliveryDateStr = str(startdeliveryDate) 
                        elif deliveryDate[0] != deliveryDate[1]:
                            startdeliveryDate= int(deliveryDate[0])
                            enddeliveryDate = int(deliveryDate[1])
                            deliveryDateStr = str(startdeliveryDate) + ","+ str(enddeliveryDate)


                        deliveryTime = int(columnDetails[4]['columnNumber'])
                        deliveryPlant = int(columnDetails[5]['columnNumber'])  

                        for column in data.columns:
                            # Check if any value in the column is NaN
                            if data[column].isnull().any():
                                # Substitute NaN values with "NULL"
                                data[column] = data[column].fillna('NULL')

                        data.fillna('', inplace=True)
                        # Convert column names to strings
                        data.columns = data.columns.astype(str)

                        print("data.columns here is ",data.columns)
                        # Clean the data
                        for column in data.columns:
                            data[column] = data[column].replace({'="': '', '"': ''}, regex=True)
                            if data[column].dtype == 'object':
                                data[column] = data[column].apply(lambda x: str(int(x)) if isinstance(x, str) and x.isdigit() else x)
                        
                        print("data here is ", data)


                        date_dict = {}

                        
                        print("startOrderQty ",startOrderQty)
                        print("endOrderQty ",endOrderQty)

                        for i in range(int(startOrderQty), int(endOrderQty)+1):
                            date_dict[i] = startDate
                            startDate = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                            

                        print("date_dict ", date_dict)
                        
                        # Melting the DataFrame
                        melted_data = data.melt(id_vars=data.columns[:2],var_name=deliveryDateStr, value_name=orderQtyStr)

                        #melted_data[deliveryDateStr] = range(1, len(melted_data) + 1)
                        print("melted_data[deliveryDateStr] ", melted_data[deliveryDateStr])
                        deli_date = melted_data[deliveryDateStr]
                        print("deli_date ",deli_date)
                        for i, val in deli_date.items():
                            print("i ", i,"val" , val)
                            val = int(val)
                            if val in date_dict.keys():
                                print("date_dict[val] ",date_dict[val])
                                melted_data.at[i, deliveryDateStr] = date_dict[val]
                                print("melted_data.at[i, deliveryDateStr] ",melted_data.at[i, deliveryDateStr])
                        
                        # Display the transformed DataFrame
                        print("Transformed DataFrame:\n", melted_data) 

                        filtered_df = melted_data[melted_data[orderQtyStr] != 0]
                        filtered_df.reset_index(drop=True, inplace=True)
                        

                        # Print the filtered DataFrame
                        print(filtered_df)

                        return JsonResponse({'template': serialized_templates, 'data': melted_data.to_dict(), 'result': filtered_df.to_dict()})

                #---------------------For Special Templates-------------------------#
                sp_templates = TemplateSpecial.objects.filter(templateID=templateSelect)
                if sp_templates:
                    serialized_templates = []
                    current_template = None
                    for template in sp_templates:
                        if current_template is None or template.templateID != current_template['templateID']:
                            if current_template is not None:
                                serialized_templates.append(current_template)
                            current_template = {
                                'templateID': template.templateID,
                                'templateName': template.templateName,
                                'startRow': template.startRow,
                                'fileType': template.fileType,
                                'templateType': template.templateType,
                                'needBackupData': template.needBackupData,
                                'columnDetails': []
                            }
                        current_template['columnDetails'].append({
                            'columnName': template.columnName,
                            'columnNumber': template.columnNumber,
                        })

                    if current_template is not None:
                        serialized_templates.append(current_template)

                    columns_to_read = set()
                    for number in current_template['columnDetails']:
                        if number['columnNumber'] and number['columnNumber'] != "0":
                            if "," in number['columnNumber']:
                                for num in number['columnNumber'].split(','):
                                    columns_to_read.add(int(num))
                            else:
                                columns_to_read.add(int(number['columnNumber']))

                    columns_to_read = sorted(columns_to_read)

                    start_row = current_template['startRow']
                    fileType = current_template['fileType']

                    if fileType == "csv":
                        data = pd.read_csv(file_path, header=None, usecols=columns_to_read, skiprows=start_row)
                    elif fileType == "txt":
                        data = pd.read_csv(file_path, sep='|', header=None, usecols=columns_to_read, skiprows=start_row)
                    elif fileType == "xls" or fileType == "xlsx":
                        data = pd.read_excel(file_path, usecols=columns_to_read, skiprows=start_row)
                    else:
                        return HttpResponse("Unsupported file type", status=400)

                    columnDetails = current_template['columnDetails']
                    customerCode = int(columnDetails[0]['columnNumber'])
                    customerPartNumber = int(columnDetails[1]['columnNumber'])
                    deliveryPlant = int(columnDetails[5]['columnNumber'])

                    data.dropna(subset=[customerPartNumber], inplace=True)

                    orderQty_list = columnDetails[2]['columnNumber'].split(',')
                    deliveryDate_list = columnDetails[3]['columnNumber'].split(',')

                    orderQty_list = list(map(int, orderQty_list))
                    deliveryDate_list = list(map(int, deliveryDate_list))

                    columns_needed = set()

                    for deliveryDate_col in deliveryDate_list:
                        for i in range(6):
                            day = int(deliveryDate_col) + i
                            columns_needed.add(day)

                    for orderQty_col in orderQty_list:
                        for i in range(6):
                            qty_col = int(orderQty_col) + i
                            columns_needed.add(qty_col)

                    columns_needed = list(columns_needed)
                    columns_needed.extend([customerCode, customerPartNumber, deliveryPlant])
                    columns_needed = sorted(set(columns_needed))
                    print("columns_needed ", columns_needed)

                    if fileType == "csv":
                        data = pd.read_csv(file_path, header=None, usecols=columns_needed, skiprows=start_row)
                    elif fileType == "txt":
                        data = pd.read_csv(file_path, sep='|', header=None, usecols=columns_needed, skiprows=start_row)
                    elif fileType == "xls" or fileType == "xlsx":
                        data = pd.read_excel(file_path, usecols=columns_needed, skiprows=start_row)
                    else:
                        return HttpResponse("Unsupported file type", status=400)

                    data.dropna(subset=[customerPartNumber], inplace=True)

                    results = []

                    for deliveryDate_col in deliveryDate_list:
                        for orderQty_col in orderQty_list:
                            for i in range(6):
                                day_col = int(deliveryDate_col) + i
                                qty_col = int(orderQty_col) + i
                                if day_col in data.columns and qty_col in data.columns:
                                    delivery_data = data[[day_col, qty_col, customerCode, customerPartNumber, deliveryPlant]].dropna()
                                    delivery_data.columns = ['DeliveryDate', 'OrderQty', 'CustomerCode', 'CustomerPartNumber', 'DeliveryPlant']
                                    results.append(delivery_data)

                    combined_data = pd.concat(results)

                    combined_data['DeliveryDate'] = combined_data['DeliveryDate'].astype(str).str.replace('.0', '')
                    combined_data = combined_data[combined_data['OrderQty'] != 0]
                    combined_data.reset_index(drop=True, inplace=True)

                    # Get the values for the new column names
                    customerCodeStr = columnDetails[0]['columnNumber']
                    customerPartNumberStr = columnDetails[1]['columnNumber']
                    orderQtyStr = columnDetails[2]['columnNumber']
                    deliveryDateStr = columnDetails[3]['columnNumber']
                    deliveryPlantStr = columnDetails[5]['columnNumber']

                    # Rename the columns
                    combined_data = combined_data.rename(columns={
                        'DeliveryDate': deliveryDateStr,
                        'OrderQty': orderQtyStr,
                        'CustomerCode': customerCodeStr,
                        'CustomerPartNumber': customerPartNumberStr,
                        'DeliveryPlant': deliveryPlantStr,
                    })

                    print(combined_data)

                    return JsonResponse({'template': serialized_templates, 'data': combined_data.to_dict(), 'result': combined_data.to_dict()})



            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            
        else:
            return JsonResponse({'error': 'No file found'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def special_template(request):
    if request.method == 'POST':
        try:
            '''latest_template = TemplateSpecial.objects.order_by('-templateID').first()
            if latest_template:
                next_template_id = latest_template.templateID + 1
            else:
                next_template_id = 1'''
            with transaction.atomic():
                latest_normal_template = TemplateActualNormal.objects.order_by('-templateID').first()
                latest_special_template = TemplateSpecial.objects.order_by('-templateID').first()
                
                if latest_normal_template and latest_special_template:
                    next_template_id = max(latest_normal_template.templateID, latest_special_template.templateID) + 1
                elif latest_normal_template:
                    next_template_id = latest_normal_template.templateID + 1
                elif latest_special_template:
                    next_template_id = latest_special_template.templateID + 1
                else:
                    next_template_id = 1
            

            data = json.loads(request.body)
            templateName = data.get('templateName')
            templateType = data.get('templateType')
            rowStarted = data.get('rowStarted')
            columnNames = data.get('columnNames')
            columnNumbers = data.get('columnNumbers')
            fileType = data.get('fileType')
            needBackupData = data.get('needBackupData')
            
           # Zip column names and numbers into a list of dictionaries
            columns = [dict(zip(columnNames, columnNumbers))]

            # Iterate over the list of dictionaries and create TemplateActualNormal instances
            for item in columns:
                for name, number in item.items():
                    new_special_template = TemplateSpecial(
                        templateID=next_template_id,
                        templateName=templateName,
                        templateType=templateType,
                        startRow=rowStarted,
                        fileType=fileType,
                        columnName=name,
                        columnNumber=number,
                        needBackupData=needBackupData,
                    )
                    new_special_template.save()
            
            print("New special template(s) successfully created")
            return redirect('templates')  # Assuming 'templates' is the name of the URL pattern you want to redirect to
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def get_special_templates(request):
    # Retrieve all TemplateActualNormal instances from the database
    templates = TemplateSpecial.objects.all()

    # Serialize the templates data into JSON
    serialized_templates = []
    for template in templates:
        serialized_templates.append({
            'templateID': template.templateID,
            'templateName': template.templateName,
            'templateType': template.templateType,
            'startRow': template.startRow,
            'fileType': template.fileType,
            'columnName': template.columnName,
            'columnNumber' : template.columnNumber,
            'needBackupData' : template.needBackupData,
        })
    
    # Return the serialized templates data as JSON response
    return JsonResponse(serialized_templates, safe=False)

def delete_special_template(request, template_id):
    if request.method == 'DELETE':
        try:
            # Retrieve all rows with the specified templateID
            templates = TemplateSpecial.objects.filter(templateID=template_id)
        except TemplateSpecial.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Template not found'})

        # Delete all rows
        templates.delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def update_special_template(request, template_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        try:
            #templates = TemplateActualNormal.objects.get(templateID=template_id)
            templates = TemplateSpecial.objects.filter(templateID=template_id)

        except TemplateSpecial.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Template not found'})

        column_names = data.get('columnNames', [])
        column_numbers = data.get('columnNumbers', [])

        if len(column_names) != len(column_numbers):
            return JsonResponse({'status': 'error', 'message': 'Column names and numbers lists must have the same length'})

        # Loop through each template in the queryset and update its fields
        for i, template in enumerate(templates):
            template.templateID = data.get('templateID', template.templateID)
            template.templateName = data.get('templateName', template.templateName)
            template.templateType = data.get('templateType', template.templateType)
            template.startRow = data.get('rowStarted', template.startRow)
            template.columnName = column_names[i] if i < len(column_names) else template.columnName
            template.columnNumber = column_numbers[i] if i < len(column_numbers) else template.columnNumber
            template.fileType = data.get('fileType', template.fileType)
            template.condition = data.get('condition', template.condition)
            template.amountdaysplus = data.get('amountdaysplus', template.amountdaysplus)
            template.columnNumberplus = data.get('columnNumberplus', template.columnNumberplus)
            template.needBackupData = data.get('needBackupData', template.needBackupData)

            template.save()


        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 

def save_customer_orders(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
            print("data is ",data)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        customer_orders_data = data.get('customerOrders', [])

        for order_data in customer_orders_data:
            order = CustomerOrder(
                templateName=order_data.get('templateName'),
                customerCode=order_data.get('customerCode'),
                customerPartNumber=order_data.get('customerPartNumber'),
                orderQuantity=order_data.get('orderQuantity'),
                deliveryDate=order_data.get('deliveryDate'),
                deliveryTime=order_data.get('deliveryTime'),
                deliveryPlant=order_data.get('deliveryPlant'),
                templateID=order_data.get('templateID')
            )
            order.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def save_customer_orders_forecast(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
            print("data is ",data)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        customer_orders_data = data.get('customerOrders', [])

        for order_data in customer_orders_data:
            order = CustomerOrderForecast(
                templateName=order_data.get('templateName'),
                customerCode=order_data.get('customerCode'),
                customerPartNumber=order_data.get('customerPartNumber'),
                orderQuantity=order_data.get('orderQuantity'),
                deliveryDate=order_data.get('deliveryDate'),
                deliveryTime=order_data.get('deliveryTime'),
                deliveryPlant=order_data.get('deliveryPlant'),
                templateID=order_data.get('templateID')
            )
            order.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def orderPlan_form(request):
    return render(request,'orderPlan.html')

def get_customerOrder_frame(request, customerName):
    try:
        customerData = CustomerData.objects.filter(customerName=customerName)
        # Initialize defaultdict to store customer orders
        customerOrders_Arr = defaultdict(lambda: defaultdict(int))
        # Dictionary to keep track of already processed customerPartNumbers for each templateID and templateName
        processed_customers = defaultdict(set)

        # Iterate over CustomerData
        for cd in customerData:
            print("Processing CustomerData entry:", cd)
            print("Filtering with customerPartNumber:", cd.customerPartNumber, "and templateID:", cd.templateID)
            
            # Check if the customerPartNumber has already been processed for this templateID and templateName
            if cd.customerPartNumber not in processed_customers[(cd.templateID, cd.templateName)]:
                print("templateID is ", cd.templateID)
                print("templateName is ", cd.templateName)
                print("customerPartNumber is ", cd.customerPartNumber)

                # Strip whitespace for debugging
                customer_part_number = cd.customerPartNumber.strip()
                template_id = cd.templateID.strip()

                # Get orders from CustomerOrder
                orders = CustomerOrder.objects.filter(customerPartNumber=customer_part_number, templateID=template_id)

                last_delivery_date = None

                for order in orders:
                    print("order in the loop is ", order)
                    key = (cd.customerPartNumber, cd.templateID, cd.SNSSPartNumber)
                    print("key here is ", key)
                    print("order.deliveryDate ", order.deliveryDate)
                    delivery_date = order.deliveryDate.replace('-', '') if '-' in order.deliveryDate else order.deliveryDate
                    customerOrders_Arr[key][delivery_date] += order.orderQuantity
                    print("customerOrders_Arr[key][order.deliveryDate] ", customerOrders_Arr[key][delivery_date])
                    # Track the last delivery date
                    if last_delivery_date is None or delivery_date > last_delivery_date:
                        last_delivery_date = delivery_date

                # If there are no orders, set last_delivery_date to an empty string
                if last_delivery_date is None:
                    last_delivery_date = ''

                # Get forecast orders from CustomerOrderForecast
                orders_forecast = CustomerOrderForecast.objects.filter(customerPartNumber=customer_part_number, templateID=template_id)

                for forecast in orders_forecast:
                    forecast_delivery_date = forecast.deliveryDate.replace('-', '') if '-' in forecast.deliveryDate else forecast.deliveryDate
                    # Add forecast order only if the forecast delivery date is after the last order delivery date
                    if forecast_delivery_date > last_delivery_date:
                        print("forecast in the loop is ", forecast)
                        key = (cd.customerPartNumber, cd.templateID, cd.SNSSPartNumber)
                        print("key here is ", key)
                        print("forecast.deliveryDate ", forecast.deliveryDate)
                        customerOrders_Arr[key][forecast_delivery_date] += forecast.orderQuantity
                        print("customerOrders_Arr[key][forecast.deliveryDate] ", customerOrders_Arr[key][forecast_delivery_date])

                processed_customers[(cd.templateID, cd.templateName)].add(cd.customerPartNumber)
            print("processed_customers ", processed_customers)
            print("processed_customers.items() are ", processed_customers.items())
            print("customerOrders_Arr.items() are ", customerOrders_Arr.items())

        # Combine orders for the same customer
        combined_customer_orders = defaultdict(dict)
        for (customerPartNumber, templateID, snssPartNumber), orders in customerOrders_Arr.items():
            customer_key = f"{snssPartNumber} {customerPartNumber}"
            combined_customer_orders[customer_key]['orders'] = orders
            combined_customer_orders[customer_key]['custPartNo'] = customerPartNumber
            combined_customer_orders[customer_key]['snssPartNo'] = snssPartNumber

        # Construct the response JSON
        customerOrders_List = [
            {
                'custPartNo': details['custPartNo'],
                'snssPartNo': details['snssPartNo'],
                'customer': customer_key,
                'orders': [
                    {'deliveryDate': deliveryDate, 'orderQty': orderQuantity}
                    for deliveryDate, orderQuantity in sorted(details['orders'].items())
                ]
            }
            for customer_key, details in combined_customer_orders.items()
        ]

        print("customerOrders_List ", customerOrders_List)

        return JsonResponse(customerOrders_List, safe=False)
    except CustomerData.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Customer data not found'}) 

    
def master_customer_data(request):
    return render(request,'customerdata.html')  

def save_customer_data(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        cusdata = CustomerData(
                customerName=data.get('customerName'),
                customerCode=data.get('customerCode'),
                templateName=data.get('templateName'),
                customerPartNumber=data.get('customerPartNo'),
                SNSSPartNumber=data.get('SNSSPartNo'),
                category=data.get('category'),
                templateID=data.get('templateID'),
            )
        cusdata.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def get_all_customer_data(request):
    custdata = CustomerData.objects.all()

    # Serialize the templates data into JSON
    serialized_customerData = []
    for cdata in custdata:
        serialized_customerData.append({
            'id': cdata.id,  # Get the id attribute
            'customerName': cdata.customerName,
            'customerCode': cdata.customerCode,
            'templateName': cdata.templateName,
            'customerPartNo': cdata.customerPartNumber,
            'SNSSPartNo': cdata.SNSSPartNumber,
            'category': cdata.category,
            'templateID': cdata.templateID,
        })

    return JsonResponse(serialized_customerData, safe=False)


def update_customer_data(request, customer_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

        try:
            customer_data = CustomerData.objects.get(id=customer_id)
        except CustomerData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer data not found'})

        # Update customer data fields
        customer_data.customerName = data.get('customerName', customer_data.customerName)
        customer_data.customerCode = data.get('customerCode', customer_data.customerCode)
        customer_data.templateName = data.get('templateName', customer_data.templateName)
        customer_data.customerPartNumber = data.get('customerPartNo', customer_data.customerPartNumber)
        customer_data.SNSSPartNumber = data.get('SNSSPartNo', customer_data.SNSSPartNumber)
        customer_data.category = data.get('category', customer_data.category)
        customer_data.templateID = data.get('templateID', customer_data.templateID)

        customer_data.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def delete_customer_data(request, customer_id):
    if request.method == 'DELETE':
        try:
            customer_data = CustomerData.objects.get(id=customer_id)
        except CustomerData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer data not found'})

        customer_data.delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def get_all_customer_names(request):
    customerData = CustomerData.objects.all()

    customer_template_map = {}
    for cdata in customerData:
        if cdata.customerName not in customer_template_map:
            customer_template_map[cdata.customerName] = {}
        customer_template_map[cdata.customerName][cdata.templateID] = cdata.templateName

    return JsonResponse(customer_template_map, safe=False)

def get_nsk_group_customers_master(request):
    # Fetch distinct customer names filtered by category "NSK"
    customerData = CustomerData.objects.filter(category="NSK").values_list('customerCode', flat=True).distinct()
    
    # Convert QuerySet to list for JsonResponse
    customerNames = list(customerData)
    
    return JsonResponse(customerNames, safe=False)

def get_all_customer_Part_Numbers_master(request,customerCode):
    customerData = CustomerData.objects.filter(customerCode=customerCode)

    customerPartNumbers = []
    for cdata in customerData:
        if cdata.customerPartNumber not in customerPartNumbers:
            customerPartNumbers.append(cdata.customerPartNumber)

    return JsonResponse(customerPartNumbers, safe=False)

def test_tt(request):
    return render(request,'test.html')   

def stock_file_upload(request): 
    if request.method == 'POST':
        if 'file' in request.FILES:
            # Upload the file
            uploaded_file = request.FILES['file']
            save_path = 'D:/Freya/production_control_project/pc_project_env/the_project/media_files'
            # Ensure the directory exists
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            file_path = os.path.join(save_path, uploaded_file.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Get the current date and time
            current_datetime = datetime.now()
            day = current_datetime.day
            print(day)
        
            today = day + 40  # This seems to be the desired column offset
            snss_partNo = 6  # Hardcoded column index
            line_info = 108
            
            columns_to_read = [snss_partNo, today, line_info]
            print("columns_to_read first ", columns_to_read)

            start_row = 1  # Assuming this is the first data row (excluding header)
            try:
                data = pd.read_csv(file_path, header=None, usecols=columns_to_read, skiprows=start_row)
                print("data before processing", data)

                # Drop rows where all elements are empty
                data.dropna(how='all', inplace=True)
                
                # Clean up strings in the DataFrame
                data[snss_partNo] = data[snss_partNo].astype(str).apply(lambda x: x.replace(' ', '').strip())
                
                # Convert float values to int if they are effectively integers
                data[today] = data[today].apply(lambda x: int(x) if x == int(x) else x)

                # Convert float values to int if they are effectively integers
                data[line_info] = data[line_info].apply(lambda x: int(x) if x == int(x) else x)
                
                print("data after processing", data)
                data.fillna('', inplace=True)

                # Exclude rows where snss_partNo column has value "0"
                data = data[data[snss_partNo] != "0"]

                new_data = pd.DataFrame(data)

                return JsonResponse({'status': 'success', 'data': new_data.to_dict()})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'No file uploaded'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
from django.utils.timezone import now

def save_stock_data(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        
        oldest_date_import_str = StockData.objects.order_by('dateImport').values_list('dateImport', flat=True).first()
        
        # Convert oldest_date_import_str to a date object
        if oldest_date_import_str:
            oldest_date_import = datetime.strptime(oldest_date_import_str, '%Y-%m-%d').date()
        else:
            oldest_date_import = None
        
        # Calculate the difference between today's date and the oldest dateImport
        if oldest_date_import:
            days_difference = (datetime.now().date() - oldest_date_import).days
        else:
            days_difference = 0
        
        # Check if the difference is greater than 31 days and delete rows if necessary
        if days_difference > 31:
            oldest_date_to_keep = datetime.now().date() - timedelta(days=31)
            StockData.objects.filter(dateImport__lt=oldest_date_to_keep).delete()
 
        latest_snssPartID = StockData.objects.order_by('-snssPartID').first()
        if latest_snssPartID:
            next_snssPart_id = latest_snssPartID.snssPartID + 1
        else:
            next_snssPart_id = 1
        
        # Get today's date
        today_date = now().date()
        
        # Store the new data
        stockdata = StockData(
            snssPartID=next_snssPart_id,
            snssPartNumber=data.get('snssPartNumber'),
            stockQty=data.get('stockQty'),
            lineInfo=data.get('lineInfo'),
            dateImport=today_date,
        )
        stockdata.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_stockData_for_tdy(request):
    today_date = now().date()
    stockDataobjs = StockData.objects.filter(dateImport=today_date)

    todayStocks = {}
    for stockDataobj in stockDataobjs:
        todayStocks[stockDataobj.snssPartNumber] = stockDataobj.stockQty

    return JsonResponse(todayStocks, safe=False)