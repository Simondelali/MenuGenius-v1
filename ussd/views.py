from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 

from .models import MenuOption, Menu

# views.py

active_sessions = {}

class USSDSession:
    def __init__(self):
        self.state = 'start'
        self.user_data = {}

def ussd_endpoint(request):
    if request.method == 'GET':
        # Create or retrieve USSD session object for the user
        session_id = request.GET.get('session_id')
        if session_id in active_sessions:
            session = active_sessions[session_id]
        else:
            session = USSDSession()
            active_sessions[session_id] = session

        # Parse incoming USSD request
        ussd_input = request.GET.get('text', '')

        # Process USSD request based on current state
        response = process_input(session, ussd_input) 

        # Send USSD response
        return HttpResponse(response)

def process_input(session, input):
    if session.state == 'start':
        response = "CON Welcome to Sample USSD App. Select a menu:\n"
        menus = Menu.objects.all()
        for i, menu in enumerate(menus, start=1):
            response += f"{i}. {menu.name}\n"
        session.state = 'select_menu'
    elif session.state == 'select_menu':
        try:
            selected_menu_index = int(input)
            selected_menu = Menu.objects.all()[selected_menu_index - 1]
            session.selected_menu = selected_menu
            options = selected_menu.menuoption_set.filter(parent_option=None)  # Only top-level options
            response = "CON Choose an option:\n"
            for i, option in enumerate(options, start=1):
                response += f"{i}. {option.name}\n"
            session.state = 'select_option'
        except (ValueError, IndexError):
            response = "END Invalid input. Please select a valid menu option."
    elif session.state == 'select_option':
        try:
            selected_option_index = int(input)
            selected_option = session.selected_menu.menuoption_set.filter(parent_option=None)[selected_option_index - 1]
            sub_options = selected_option.child_options.all()
            if sub_options.exists():
                response = "CON Choose a sub-option:\n"
                for i, sub_option in enumerate(sub_options, start=1):
                    response += f"{i}. {sub_option.name}\n"
                session.state = 'select_sub_option'
            else:
                response = f"END You selected: {selected_option.name}. Value: {selected_option.value}"
                session.state = 'start'
        except (ValueError, IndexError):
            response = "END Invalid input. Please select a valid option."
    elif session.state == 'select_sub_option':
        try:
            selected_sub_option_index = int(input)
            selected_sub_option = session.selected_menu.menuoption_set.filter(parent_option=None)[selected_sub_option_index - 1]
            response = f"END You selected: {selected_sub_option.name}. Value: {selected_sub_option.value}"
            session.state = 'start'
        except (ValueError, IndexError):
            response = "END Invalid input. Please select a valid sub-option."

    return response

