from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Client, Lead, Meeting, Sale
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from django.http import HttpResponseForbidden
import pandas as pd
from .models import Client
from .forms import FileUploadForm, AddClientForm

from django.db.models import Count, Sum
import json

@login_required
def client_list(request):
    if request.user.is_superuser:
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(relationship_manager=request.user)

    # Pagination
    paginator = Paginator(clients, 20)  # Show 10 clients per page
    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)  # Get the clients for the current page

    return render(request, 'crm/client_list.html', {'page_obj': page_obj})

#upload bulk client

@login_required
def upload_clients(request):
    # Allow access only for superusers
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)

            for _, row in data.iterrows():
                # Adjust these to match your CSV/Excel column names
                name = row['Name']
                email = row['Email']
                phone = row['Phone']
                pan = row.get('PAN', '')  # Read PAN column
                manager_first_name = row['Relationship Manager First Name']
                manager_last_name = row['Relationship Manager Last Name']

                # Get the relationship manager based on their first and last name
                manager = User.objects.filter(
                    first_name=manager_first_name,
                    last_name=manager_last_name
                ).first()

                # Create the client object
                Client.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    pan=pan,  # Save PAN
                    relationship_manager=manager
                )
            return redirect('success_page')  # Replace with an appropriate success URL

    else:
        form = FileUploadForm()

    return render(request, 'crm/upload_clients.html', {'form': form})

#add single client


 # Create this form for adding clients


@login_required
def add_client(request):
    # Allow access only for superusers
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    if request.method == "POST":
        form = AddClientForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            pan = form.cleaned_data.get('pan', '')  # Optional PAN field
            manager_id = form.cleaned_data['relationship_manager']

            # Get the relationship manager (if provided)
            manager = User.objects.filter(id=manager_id).first()

            # Create the client object
            Client.objects.create(
                name=name,
                email=email,
                phone=phone,
                pan=pan,  # Save PAN
                relationship_manager=manager,
            )
            return redirect('success_page')  # Replace with a success URL or client list page

    else:
        form = AddClientForm()

    return render(request, 'crm/add_client.html', {'form': form})
#@login_required
def home(request):
    return render(request, 'crm/home.html')  # Adjust the template path as necessary

@login_required
def add_meeting(request, client_id):
    # Allow superusers to access all clients
    if request.user.is_superuser:
        client = get_object_or_404(Client, id=client_id)
    else:
        client = get_object_or_404(Client, id=client_id, relationship_manager=request.user)

    if request.method == 'POST':
        date = request.POST.get('date')
        notes = request.POST.get('notes')
        remark = request.POST.get('remark')

        Meeting.objects.create(
            client=client,
            relationship_manager=request.user,
            date=date,
            notes=notes,
            remark=remark,
        )
        return redirect('client_list')  # Redirect to client list or another page

    return render(request, 'crm/add_meeting.html', {'client': client})

#update meeting remark
@login_required
def update_meeting_remark(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, relationship_manager=request.user)
    if request.method == 'POST':
        remark = request.POST.get('remark')
        if remark in ['Completed', 'Pending']:
            meeting.remark = remark
            meeting.save()
        return redirect('client_list')
    return render(request, 'crm/update_meeting_remark.html', {'meeting': meeting})

#update meeting
@login_required
def update_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.method == 'POST':
        meeting.date = request.POST.get('date', meeting.date)
        meeting.notes = request.POST.get('notes', meeting.notes)
        meeting.remark = request.POST.get('remark', meeting.remark)
        meeting.save()
        return redirect('meetings_list')  # Replace with the appropriate redirect
    return render(request, 'crm/update_meeting.html', {'meeting': meeting})

#delete Meeting
@login_required
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if request.method == 'POST':
        meeting.delete()
        return redirect('meetings_list')  # Replace with the appropriate redirect
    return render(request, 'crm/delete_meeting.html', {'meeting': meeting})



@login_required
def add_sale(request, client_id):
    # Ensure the client is assigned to the logged-in user
    client = get_object_or_404(Client, id=client_id, relationship_manager=request.user)
    if request.method == 'POST':
        product = request.POST.get('product')
        fund_name = request.POST.get('fund_name')
        amount = request.POST.get('amount')

        sale_date = request.POST.get('sale_date')
        Sale.objects.create(client=client, product=product, fund_name=fund_name,amount=amount, sale_date=sale_date)
        return redirect('client_list')
    return render(request, 'crm/add_sales.html', {'client': client})

@login_required
def add_sale(request, client_id):
    # Allow superusers to access all clients
    if request.user.is_superuser:
        client = get_object_or_404(Client, id=client_id)
    else:
        client = get_object_or_404(Client, id=client_id, relationship_manager=request.user)

    if request.method == 'POST':
        product = request.POST.get('product')
        fund_name = request.POST.get('fund_name')
        amount = request.POST.get('amount')
        sale_date = request.POST.get('sale_date')

        Sale.objects.create(
            client=client,
            product=product,
            fund_name=fund_name,
            amount=amount,
            sale_date=sale_date,
        )
        return redirect('client_list')

    return render(request, 'crm/add_sales.html', {'client': client})
# @login_required
# def meetings_list(request, client_id=None):
#     if request.user.is_superuser:
#         # Superusers see all meetings
#         meetings = Meeting.objects.select_related('client', 'relationship_manager').all()
#         client = None  # No specific client for superusers
#     else:
#         if not client_id:
#             return redirect('client_list')  # Redirect if client_id is missing
#         # Fetch the client and their associated meetings
#         client = get_object_or_404(Client, id=client_id, relationship_manager=request.user)
#         meetings = Meeting.objects.filter(client=client).select_related('relationship_manager')
#
#     return render(request, 'crm/meetings_list.html', {'meetings': meetings, 'client': client})

#meeting List
@login_required
def meetings_list(request, client_id=None):
    filter_remark = request.GET.get('remark')  # Get the filter value from the query parameters

    if request.user.is_superuser:
        # Superusers see all meetings
        meetings = Meeting.objects.select_related('client', 'relationship_manager').all()
        client = None  # No specific client for superusers
    else:
        # For relationship managers
        if client_id:
            # Fetch the client and their associated meetings
            client = get_object_or_404(Client, id=client_id, relationship_manager=request.user)
            meetings = Meeting.objects.filter(client=client, relationship_manager=request.user).select_related('relationship_manager')
        else:
            # Show all meetings managed by the logged-in relationship manager
            client = None
            meetings = Meeting.objects.filter(relationship_manager=request.user).select_related('client')

    # Apply the filtering based on the `remark` field if a filter is provided
    if filter_remark in ['Completed', 'Pending']:
        meetings = meetings.filter(remark=filter_remark)

    # Pagination
    paginator = Paginator(meetings, 20)  # Show 20 meetings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crm/meetings_list.html', {
        'page_obj': page_obj,
        'client': client,
        'filter_remark': filter_remark  # Include the current filter value for the template
    })
@login_required
def sales_list(request):
    is_relationship_manager = (
        not request.user.is_superuser and
        request.user.groups.filter(name="Relationship Managers").exists()
    )

    if request.user.is_superuser:
        # Superusers see all sales
        sales = Sale.objects.select_related('client', 'client__relationship_manager').all()
    else:
        # Normal users see only their own clients' sales
        sales = Sale.objects.filter(client__relationship_manager=request.user).select_related('client', 'client__relationship_manager')

    # Apply filters
    relationship_manager = request.GET.get('relationship_manager')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    product = request.GET.get('product')

    if relationship_manager:
        first_name, *last_name = relationship_manager.split()
        sales = sales.filter(client__relationship_manager__first_name__icontains=first_name)
        if last_name:
            sales = sales.filter(client__relationship_manager__last_name__icontains=' '.join(last_name))
    if start_date and end_date:
        sales = sales.filter(sale_date__range=[start_date, end_date])
    elif start_date:
        sales = sales.filter(sale_date__gte=start_date)
    elif end_date:
        sales = sales.filter(sale_date__lte=end_date)
    if product:
        sales = sales.filter(product__icontains=product)

    # Pagination
    paginator = Paginator(sales, 20)  # Show 20 sales per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crm/sales_list.html', {
        'page_obj': page_obj,
        'is_relationship_manager': is_relationship_manager,
        'relationship_manager': relationship_manager,
        'start_date': start_date,
        'end_date': end_date,
        'product': product,
    })
from django.db.models import Count, Sum

# @login_required
# def admin_dashboard(request):
#     if not request.user.is_superuser:
#         return redirect('home')  # Restrict access to only superusers
#
#     # Aggregating data for Relationship Managers
#     managers_data = (
#         User.objects.filter(groups__name='Relationship Manager')  # Only fetch relationship managers
#         .annotate(
#             total_meetings=Count('meetings', distinct=True),  # Count meetings related to each manager
#             total_sales=Count('clients__sales', distinct=True),  # Count sales through related clients
#             total_calls=Count('clients__leads', distinct=True)  # Example: Count leads as calls (if applicable)
#         )
#         .values('id', 'first_name', 'last_name', 'total_meetings', 'total_sales', 'total_calls')
#     )
#
#     return render(request, 'crm/admin_dashboard.html', {'managers_data': managers_data})




# Admin Dashboard




@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')  # Restrict access to only superusers

    # Dynamically fetch users who are "relationship managers"
    relationship_managers = User.objects.filter(
        id__in=Client.objects.values('relationship_manager').distinct()
    )

    # Filter data based on the selected relationship manager
    selected_manager_id = request.GET.get('relationship_manager_id')
    if selected_manager_id:
        managers_data = (
            User.objects.filter(id=selected_manager_id)
            .annotate(
                total_meetings=Count('meetings', distinct=True),
                total_sales=Count('clients__sales', distinct=True),
            )
            .values('id', 'first_name', 'last_name', 'total_meetings', 'total_sales')
        )
    else:
        # Default: Fetch aggregated data for all managers
        managers_data = (
            relationship_managers.annotate(
                total_meetings=Count('meetings', distinct=True),
                total_sales=Count('clients__sales', distinct=True),
            )
            .values('id', 'first_name', 'last_name', 'total_meetings', 'total_sales')
        )

    # Serialize data for charts
    serialized_data = json.dumps(list(managers_data))

    # Pass data to the template
    return render(request, 'crm/admin_dashboard.html', {
        'managers_data': serialized_data,
        'relationship_managers': relationship_managers,
        'selected_manager_id': selected_manager_id,
    })

# export meeting data in excel
from openpyxl import Workbook
from django.http import HttpResponse

@login_required
def export_meetings_to_excel(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Create an Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Meetings"

    # Add headers
    headers = ["Client Name", "Relationship Manager", "Date", "Notes", "Remark"]
    sheet.append(headers)

    # Add data
    meetings = Meeting.objects.select_related('client', 'relationship_manager').all()
    for meeting in meetings:
        sheet.append([
            meeting.client.name,
            meeting.relationship_manager.get_full_name() if meeting.relationship_manager else "Not Assigned",
            meeting.date.strftime('%Y-%m-%d') if meeting.date else "N/A",  # Format the date
            meeting.notes,
            meeting.remark,
        ])

    # Prepare HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="meetings.xlsx"'
    workbook.save(response)
    return response
#export sales data to excel


@login_required
def export_sales_to_excel(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Create an Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sales"

    # Add headers
    headers = ["Client Name", "Relationship Manager", "Product", "Fund Name", "Amount", "Sale Date"]
    sheet.append(headers)

    # Add data
    sales = Sale.objects.select_related('client', 'client__relationship_manager').all()
    for sale in sales:
        sheet.append([
            sale.client.name,
            sale.client.relationship_manager.get_full_name() if sale.client.relationship_manager else "Not Assigned",
            dict(Sale.PRODUCT_CHOICES).get(sale.product, sale.product),  # Get full product name
            sale.fund_name if sale.product == "SIP" else "N/A",  # Include fund name for SIP, otherwise N/A
            float(sale.amount),  # Convert Decimal to float for Excel
            sale.sale_date.strftime('%Y-%m-%d') if sale.sale_date else "N/A",  # Format date as string
        ])

    # Prepare HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="sales.xlsx"'
    workbook.save(response)
    return response

#update client

from .forms import UpdateClientForm

@login_required
def update_client(request, client_id):
    # Allow access only for superusers
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Get the client object or return 404 if not found
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        form = UpdateClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()  # Update the client details
            return redirect('client_list')  # Redirect to the client list after updating
    else:
        form = UpdateClientForm(instance=client)

    return render(request, 'crm/update_client.html', {'form': form, 'client': client})
def success_page(request):
    return render(request, 'crm/success.html')

def custom_logout_view(request):
    logout(request)
    return redirect('/')  # Redirect to the homepage
