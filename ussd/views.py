from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 

from django.views.decorators.csrf import csrf_exempt

from .models import MenuOption, Menu

# views.py

active_sessions = {}

class USSDSession:
    def __init__(self):
        self.state = 'start'
        self.user_data = {}

@csrf_exempt
def ussd_endpoint(request):
    if request.method == 'POST':
        # Retrieve or create USSD session object for the user
        session_id = request.POST.get('sessionId')
        if session_id in active_sessions:
            session = active_sessions[session_id]
        else:
            session = USSDSession()
            active_sessions[session_id] = session

        # Parse incoming USSD request
        ussd_input = request.POST.get('text', '')

        session.user_data = {'ghagshshshashsh'}

        print(active_sessions)
        print(ussd_input)
        print(session.user_data)

        # Process USSD request based on current state
        response = process_input(session, ussd_input) 

        # Send USSD response
        return HttpResponse(response)
    else:
        # Handle other HTTP methods if necessary
        return HttpResponse("Method not allowed", status=405)

def process_input(session, input):
    state_handlers = {
        'start': handle_start_state,
        'select_menu': handle_select_menu_state,
        'select_option': handle_select_option_state,
        'select_sub_option': handle_select_sub_option_state,
    }

    handler = state_handlers.get(session.state)
    if handler:
        return handler(session, input)
    else:
        return "END Invalid session state. Please start again."

def handle_start_state(session, input):
    response = "CON Welcome to Sample USSD App. Select a menu:\n"
    menus = Menu.objects.all()
    for i, menu in enumerate(menus, start=1):
        response += f"{i}. {menu.name}\n"
    session.state = 'select_menu'
    return response

def handle_select_menu_state(session, input):
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
    return response

def handle_select_option_state(session, input):
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
    return response

def handle_select_sub_option_state(session, input):
    try:
        selected_sub_option_index = int(input)
        selected_sub_option = session.selected_menu.menuoption_set.filter(parent_option=None)[selected_sub_option_index - 1]
        response = f"END You selected: {selected_sub_option.name}. Value: {selected_sub_option.value}"
        session.state = 'start'
    except (ValueError, IndexError):
        response = "END Invalid input. Please select a valid sub-option."
    return response

