##### FINAL CODE #####

# Libraries used
from math import radians, cos, sin, sqrt, asin
import requests
import random
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from tkcalendar import DateEntry

bookingQueue = []
checkQueue = []
tempChQ = [] #checking for same appointments but without name so no 2 users can book same appointment at same time at same salon
names = []
tempQ = []
waitinglst = []

# Cost for services - dummy
services = {'haircut': [random.randrange(2000, 5000, 100), 20], 'pedicure': [random.randrange(1000, 3000, 100), 20],
            'manicure': [random.randrange(1000, 3000, 100), 20], 'facials': [random.randrange(1000, 5000, 100), 20],
            'waxing': [random.randrange(1000, 2000, 50), 20],
            'hair treatments': [random.randrange(1000, 5000, 100), 20]}


# Finds salons using API - returns dictionary of all the salons
def findNearestSalons(geocodes_user2):
    url = "https://api.foursquare.com/v3/places/search"

    params = {
        "query": "salon",
        "ll": geocodes_user2,
        'limit': '50'
    }

    headers = {
        "Accept": "application/json",
        "Authorization": "fsq3h7FMZkuOpU6iJ6Xl8/+jjJCkMZsJhIzltgpSZDccUrA="
    }

    response = requests.request("GET", url, params=params, headers=headers)
    response = dict(response.json())

    return response


# Compute distance between two locations using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6372.8  # For Earth radius in kilometers use 6372.8 km

    dLat = (radians(lat2 - lat1))
    dLon = (radians(lon2 - lon1))
    lat1 = (radians(lat1))
    lat2 = (radians(lat2))

    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


# Formatting the raw data
def data_format(lat, lon, data):
    lst = []
    for res in data["results"]:
        lst1 = []
        # Removing unneccesary info
        for i, j in res.items():
            if i != 'fsq_id' and i != 'categories' and i != 'related_places' and i != 'timezone' and i != 'chains' and i != 'link':
                lst1.append(res[i])
        lst.append(lst1)

    # Creating separate lists for each parameter that we need
    geocodes = []
    names = []
    address = []
    for i in lst:
        names.append(i[3])
        address.append(i[2]['formatted_address'])
        for j, m in i[1].items():
            geocodes.append((m['latitude'], m['longitude']))

    # Calculating Distance from Latitude and Longitude - Haversine Formula
    dist = []
    for i in geocodes:
        dist.append(haversine(float(lat), float(lon), float(i[0]), float(i[1])))

    # Storing all the data in a list of dictionaries
    salons = []
    for i in range(len(names)):
        salon = {}
        salon['name'] = names[i]
        salon['proximity'] = dist[i]
        salon['address'] = address[i]
        salon['ratings'] = round(random.uniform(1.5, 5), 1)
        salons.append(salon)
    return salons


# Filters salons according to users preference
def user_pref(user_choice, salons):
    user_choice = user_choice.lower()

    # If preference - Proximity/Rating
    if user_choice == 'proximity' or user_choice == 'ratings':
        salons = quickSort(user_choice, salons)
    # If preference - Both
    elif user_choice == 'both':
        salons = sorted(salons, key=lambda x: (x['proximity'], x['ratings']))
    return salons


# Sorting Algorithm
def quickSort(user, data):
    size = len(data)
    if size < 2:
        return data
    j = 0
    for i in range(1, size):
        # Sorting according to PROXIMITY
        if user == 'proximity':
            if data[i][user] < data[0][user]:
                j += 1
                temp = data[i]
                data[i] = data[j]
                data[j] = temp
        # Sorting according to RATINGS
        elif user == 'ratings':
            if data[i][user] > data[0][user]:
                j += 1
                temp = data[i]
                data[i] = data[j]
                data[j] = temp

    temp = data[0]
    data[0] = data[j]
    data[j] = temp

    left = quickSort(user, data[0:j])
    right = quickSort(user, data[j + 1:size])

    data = left + [data[j]] + right

    return data


# Displaying Top 15 Salons
def display_salons(userpref):
    lst = []
    # Loop extracts relevant info - Salon Name, Ratings, Address  - Stored as TUPLE
    for i in range(15):
        b = userpref[i]['name'].lower()
        a = (
            userpref[i]['name'], str(round(userpref[i]['proximity'], 1)) + ' km',
            str(userpref[i]['ratings']) + ' stars',
            userpref[i]['address'])
        lst.append(a)
        names.append(b)

    # Label to display Top 15 Salons
    lst_label = tk.Label(bookapt_window, text='Here is a list of top 15 nearest salons to you:',
                         font=('Arial', 9, 'bold'), bg='#FFE0E0')
    lst_label.pack()

    # Iterate over lst - display each salons detail in a different label
    for i, salon in enumerate(lst):
        display_label = tk.Label(bookapt_window, text=f"{i + 1}. {salon[0]} - {salon[1]} - {salon[2]} - {salon[3]}",
                                 anchor='w', bg='#FFE0E0')

        display_label.pack()


# defining queue functions
def enQueue(lst, x):
    if not (isFull(lst)):
        lst.append(x)
    return False


def isFull(lst):
    if len(lst) == 120:
        return True
    else:
        return False


def front(lst):
    return lst[0]


def isEmpty(lst):
    if len(lst) == 0:
        return True
    return False


def deQueue(lst):
    if not (isEmpty(lst)):
        lst.pop(0)


# GUI related functions (windows)
def cancelbooking(salon_entry, name_entry, service_entry, date_entry, ampm_var, hour_var, minute_var, cancel_window):
    # Gathering time variables
    hour = hour_var.get()
    minute = minute_var.get()
    ampm = ampm_var.get()

    # Getting input from gui and storing it in variables
    name = name_entry.get()
    service = (service_entry.get()).lower()
    date = date_entry.get()
    time = hour + ':' + minute + ' ' + ampm

    salon = (salon_entry.get()).lower()

    # If Booking Queue is empty OR Appointment is not in Booking Queue - Displays message
    if isEmpty(bookingQueue) or {'salon': salon, 'date': date, 'time': time, 'customer_name': name,
                                 'service_type': service} not in bookingQueue:

        confirmation_message = tk.Label(cancel_window, text='No such appointment found in our records, check if you have entered correct details.',bg='#FFCCE5',font=('Arial', 8, 'bold'))
        confirmation_message.pack()
        # adding exit button so user is redirected to the main page
        exit_button = tk.Button(cancel_window, text='Return to main page', bg='#FFCCE5', command=cancel_window.destroy)
        exit_button.pack()
    else:
        # If appointment found in Booking Queue - Iterates over queue
        while not (isEmpty(bookingQueue)):
            f = front(bookingQueue)

            # It dequeues other appointments and stores in temporary queue
            if f != {'salon': salon, 'date': date, 'time': time, 'customer_name': name, 'service_type': service}:
                a = deQueue(bookingQueue)
                b = deQueue(checkQueue)
                enQueue(tempQ, a)
                enQueue(tempChQ, b)
            # It dequeues the required appointment
            elif f == {'salon': salon, 'date': date, 'time': time, 'customer_name': name, 'service_type': service}:
                deQueue(bookingQueue)
                deQueue(checkQueue)
                # cancel_window.destroy() # destroy the cancel_window after appointment is cancelled
                confirmation_message = tk.Label(cancel_window, text='Your appointment has been cancelled!',bg='#FFCCE5',font=('Arial', 8, 'bold'))
                confirmation_message.pack()
                # adding exit button so user is redirected to the main page
                exit_button = tk.Button(cancel_window, text='Return to main page', bg='#FFCCE5',
                                        command=cancel_window.destroy)
                exit_button.pack()

        x = deQueue(waitinglst)
        # Adds other appointments - from temporary queue back to booking queue and checkApt queue
        for i in tempChQ:
            enQueue(checkQueue, i)
        for i in tempQ:
            enQueue(bookingQueue, i)
        enQueue(bookingQueue, x)
        enQueue(checkQueue, x)


def cancelapt():
    global cancel_window
    # Create a new window for the cancel appointment page
    cancel_window = tk.Toplevel(root)
    cancel_window.title('Cancel Appointment')
    cancel_window.geometry("600x600")
    cancel_window.config(bg='#FFE0E0')

    # Add entry fields for the user to enter their booking details
    name_label = tk.Label(cancel_window, text='Name:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
    name_label.pack()
    name_entry = tk.Entry(cancel_window)
    name_entry.pack()

    salon_label = tk.Label(cancel_window, text='Salon:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
    salon_label.pack()
    salon_entry = tk.Entry(cancel_window)
    salon_entry.pack()

    service_label = tk.Label(cancel_window, text='Service:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
    service_label.pack()
    service_entry = tk.Entry(cancel_window)
    service_entry.pack()

    # Create a label and a DateEntry widget
    date_label = tk.Label(cancel_window, text="Select the date:", font=('Arial', 8, 'bold'), bg='#FFE0E0')
    date_label.pack()
    date_entry = DateEntry(cancel_window, width=12, background='purple', foreground='white', borderwidth=2)
    date_entry.pack()

    time_label = tk.Label(cancel_window, text='Time:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
    time_label.pack()

    # creating a frame to make grid in top level window
    frame = tk.Frame(cancel_window)
    frame.pack()

    hour_label = ttk.Label(frame, text="Hour:")
    hour_label.grid(row=0, column=0)

    # Create a Spinbox widget for the hour selection
    hour_var = tk.StringVar()
    hour_options = [str(i).zfill(2) for i in range(12)]
    hour_menu = ttk.OptionMenu(frame, hour_var, hour_options[0], *hour_options)
    hour_menu.grid(row=0, column=1)

    # Create a label for the minute selection
    minute_label = ttk.Label(frame, text="Minute:")
    minute_label.grid(row=1, column=0)

    # Create an OptionMenu widget for the minute selection
    minute_var = tk.StringVar()
    minute_options = [str(i).zfill(2) for i in range(60)]
    minute_menu = ttk.OptionMenu(frame, minute_var, minute_options[0], *minute_options)
    minute_menu.grid(row=1, column=1)

    # creat am/pm option and label
    ampm_label = ttk.Label(frame, text="AM/PM:")
    ampm_label.grid(row=2, column=0)
    ampm_var = tk.StringVar()
    ampm_options = ['AM', 'PM']
    ampm_menu = ttk.OptionMenu(frame, ampm_var, ampm_options[0], *ampm_options)
    ampm_menu.grid(row=2, column=1)

    cancel_button = tk.Button(cancel_window, text='Cancel Appointment', bg='#FFCCE5',
                              command=lambda: cancelbooking(salon_entry, name_entry, service_entry, date_entry,
                                                            ampm_var, hour_var, minute_var, cancel_window))
    cancel_button.pack()


def booking():
    global booking_window
    global service2
    booking_window = tk.Toplevel(root)
    booking_window.title("Booking details")
    booking_window.geometry("600x600")
    booking_window.config(bg='#FFE0E0')

    # Check salon is in list - Display message if not in list
    salon_chosen = (salon_chosen_entry.get()).lower()
    if salon_chosen not in names:
        frame2 = tk.Frame(bookapt_window)
        frame2.pack()
        wrongSal_label = tk.Label(frame2, text="Please enter a salon from the list!",
                                  font=('Arial', 9, 'bold'), fg='red')
        wrongSal_label.grid(row=0, column=0)

        # Create a button widget for user to try a salon from the list
        button = tk.Button(frame2, text="Try again", bg='#FFCCE5', command=lambda: hide_label(wrongSal_label))
        button.grid(row=1, column=0)

        def hide_label(label):
            label.grid_forget()
            button.grid_forget()
            frame2.destroy()

        booking_window.destroy()  # destroy new window if salon not in given list

    else:
        # Add entry fields for the user to enter their booking details
        name_label = tk.Label(booking_window, text='Name:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
        name_label.pack()
        name_entry = tk.Entry(booking_window)
        name_entry.pack()

        # Choosing serviv
        service_label = tk.Label(booking_window, text='Choose your desired service:', font=('Arial', 8, 'bold'),
                                 bg='#FFE0E0')
        service_label.pack()
        service_var = tk.StringVar(booking_window)
        service_var.set('Haircut')  # Default option
        service_dropdown = tk.OptionMenu(booking_window, service_var, 'Haircut', 'Pedicure', 'Manicure', 'Facials',
                                         'Waxing', 'Hair treatments')
        service_dropdown.pack()

        # Create a label and a DateEntry widget
        date_label = tk.Label(booking_window, text="Select the date:", font=('Arial', 8, 'bold'), bg='#FFE0E0')
        date_label.pack()
        date_entry = DateEntry(booking_window, width=12, background='purple', foreground='white', borderwidth=2)
        date_entry.pack()

        time_label = tk.Label(booking_window, text='Time:', font=('Arial', 8, 'bold'), bg='#FFE0E0')
        time_label.pack()

        # creating a frame to make grid in top level window
        frame = tk.Frame(booking_window)
        frame.pack()

        hour_label = ttk.Label(frame, text="Hour:")
        hour_label.grid(row=0, column=0)

        # Create a Spinbox widget for the hour selection
        hour_var = tk.StringVar()
        hour_options = [str(i).zfill(2) for i in range(12)]
        hour_menu = ttk.OptionMenu(frame, hour_var, hour_options[0], *hour_options)
        hour_menu.grid(row=0, column=1)

        # Create a label for the minute selection
        minute_label = ttk.Label(frame, text="Minute:")
        minute_label.grid(row=1, column=0)

        # Create an OptionMenu widget for the minute selection
        minute_var = tk.StringVar()
        minute_options = [str(i).zfill(2) for i in range(60)]
        minute_menu = ttk.OptionMenu(frame, minute_var, minute_options[0], *minute_options)
        minute_menu.grid(row=1, column=1)

        # creat am/pm option and label
        ampm_label = ttk.Label(frame, text="AM/PM:")
        ampm_label.grid(row=2, column=0)
        ampm_var = tk.StringVar()
        ampm_options = ['AM', 'PM']
        ampm_menu = ttk.OptionMenu(frame, ampm_var, ampm_options[0], *ampm_options)
        ampm_menu.grid(row=2, column=1)

        enter_button = tk.Button(booking_window, text='Enter', bg='#FFCCE5',
                                 command=lambda: confirmation(name_entry, service_var, date_entry, hour_var, minute_var,
                                                              ampm_var, salon_chosen, booking_window))
        enter_button.pack()


# Function takes parameters neccesary for booking
def confirmation(name_entry, service_var, date_entry, hour_var, minute_var, ampm_var, salon_chosen, booking_window):
    # gathering time variables
    hour = hour_var.get()
    minute = minute_var.get()
    ampm = ampm_var.get()

    # getting input from gui and storing it in variables
    name = name_entry.get()
    service2 = service_var.get()
    service = (service_var.get()).lower()
    date = date_entry.get()
    time = hour + ':' + minute + ' ' + ampm

    # The function retrieves the cost of the selected service from a dictionary named
    cost = services[service][0]
    # check if name is given or not
    if name == '':
        frame2 = tk.Frame(booking_window)
        frame2.pack()
        wrongName_label = tk.Label(frame2, text="Please enter your name.",
                                   font=('Arial', 9, 'bold'), fg='red')
        wrongName_label.grid(row=0, column=0)

        # Create a button widget for user to try a new location
        button = tk.Button(frame2, text="OK", bg='#FFCCE5', command=lambda: hide_label(wrongName_label))
        button.grid(row=1, column=0)

        def hide_label(label):
            label.grid_forget()
            button.grid_forget()
            frame2.destroy()

    else:  # if name given

        # Checking if appointment exists already or not - if not then book the appointment
        appointment = {'salon': salon_chosen, 'date': date, 'time': time, 'customer_name': name,
                       'service_type': service}
        checkApt = {'salon': salon_chosen, 'date': date, 'time': time, 'service_type': service} #to check if appointment exists
        if services[service][1] != 0:
            if checkApt in checkQueue:
                # If booking exists - DISPLAY MESSAGE
                    msg1_label = tk.Label(booking_window,
                                          text='Sorry, this time slot is already booked for this service! Try another time.')
                    msg1_label.pack()

                    # Enqueued to waiting list
                    wait = {'salon': salon_chosen, 'date': date, 'time': time, 'customer_name': name,
                            'service_type': service}
                    enQueue(waitinglst, wait)
            # If booking doesnt exist and queue is not full - Appointment enqueued to Booking Queue
            elif not (isFull(bookingQueue)):
                enQueue(bookingQueue, appointment)
                enQueue(checkQueue, checkApt)
                # Quantity of Available Slot decreased
                services[service][1] -= 1

                # Confirmation message
                msg1_label = tk.Label(booking_window,
                                      text=f'Your appointment has been booked! Your approximate total cost will be around Rs. {cost} depending on the type of {service}.',
                                      font=('Arial', 8, 'bold'))
                msg1_label.pack()
                msg2_label = tk.Label(booking_window,
                                      text='Note: Total cost is subject to change and will be comfirmed in person.',
                                      font=('Arial', 9, 'bold'), fg='red')
                msg2_label.pack()
                # adding exit button so user is redirected to the main page
                bookapt_window.destroy()
                exit_button = tk.Button(booking_window, text='Exit', bg='#FFCCE5', command=booking_window.destroy)
                exit_button.pack()

            else:
                # If ALL slots are full - Display message & enqueue to Waiting Queue
                msg1_label = tk.Label(booking_window,
                                      text='All slots at this salon have been booked! Try another salon.')
                msg1_label.pack()
                wait = {'salon': salon_chosen, 'date': date, 'time': time, 'customer_name': name,
                        'service_type': service, 'approximate cost': cost}
                enQueue(waitinglst, wait)

        else:
            # If selected service has no available slots
            msg1_label = tk.Label(booking_window,
                                  text='Sorry, all slots for this service have been booked! Try another service.')
            msg1_label.pack()
            wait = {'salon': salon_chosen, 'date': date, 'time': time, 'customer_name': name, 'service_type': service}
            enQueue(waitinglst, wait)


def get_location():
    global location_entry
    global salon_chosen_entry
    location = location_entry.get()
    # URL for OSM Nominatim API
    url = f"https://nominatim.openstreetmap.org/search/{location}?format=json"

    # Make a request to the OSM Nominatim API - In JSON format
    response = requests.get(url).json()

    if len(response) != 0:
        # Extract the latitude and longitude from the response
        latitude = response[0]['lat']
        longitude = response[0]['lon']

        # Formats latitude and longitude to string
        geocodes_user2 = str(latitude) + ',' + str(longitude)

        # Finds nearest salons - based on coordinate - Dictionary
        response = findNearestSalons(geocodes_user2)

        # Formatting the data
        salons = data_format(latitude, longitude, response)
        userpref = user_pref(preference_var.get(), salons)

        # Displays salons - based on users preference
        display_salons(userpref)

        # Asks user to enter their desired salon
        salon_chosen_label = tk.Label(bookapt_window, text="Choose your desired salon from the provided list:",
                                      font=('Arial', 9, 'bold'), bg='#FFE0E0')
        salon_chosen_label.pack()

        salon_chosen_entry = tk.Entry(bookapt_window)
        salon_chosen_entry.pack()

        # Booking Process - After Salon selected
        salonchosen_button = tk.Button(bookapt_window, text="Enter", bg='#FFCCE5', command=booking)
        salonchosen_button.pack()

    else:
        # To remove pop-up after correct location given
        frame1 = tk.Frame(bookapt_window)
        frame1.pack()
        wrongLoc_label = tk.Label(frame1, text="Please enter a valid location with a landmark.",
                                  font=('Arial', 9, 'bold'), fg='red')
        wrongLoc_label.grid(row=0, column=0)

        # Create a button widget
        button = tk.Button(frame1, text="Try again", bg='#FFCCE5', command=lambda: hide_label(wrongLoc_label))
        button.grid(row=1, column=0)

        def hide_label(label):
            label.grid_forget()
            button.grid_forget()
            frame1.destroy()


def bookingaptwindow():
    # Global Variables
    global location_entry
    global bookapt_window
    global preference_dropdown
    global preference_var

    # Booking Appointment Window
    bookapt_window = tk.Toplevel(root)
    bookapt_window.title("Book Appointment")
    bookapt_window.geometry("600x600")
    bookapt_window.config(bg='#FFE0E0')

    # Input Users Location
    location_label = tk.Label(bookapt_window, text="Please enter your current location:", font=('Arial', 9, 'bold'),
                              bg='#FFE0E0')
    location_label.pack()

    location_entry = tk.Entry(bookapt_window)
    location_entry.pack()

    # Users Preference - Drop-down box
    preference_label = tk.Label(bookapt_window,
                                text="Do you prefer salons' proximity to your location or ratings or both? Choose an option:",
                                bg='#FFE0E0', font=('Arial', 9, 'bold'))
    preference_label.pack()

    preference_var = tk.StringVar(bookapt_window)
    preference_var.set('Proximity')  # Default option
    preference_dropdown = tk.OptionMenu(bookapt_window, preference_var, 'Proximity', 'Ratings', 'Both')
    preference_dropdown.pack()

    # Button to Finding Nearest Salons - based on current location & preferences
    locEnter_button = tk.Button(bookapt_window, text="Find salons near me", bg='#FFCCE5', command=get_location)
    locEnter_button.pack()


# -- MAIN FUNCTION --
def final():
    # while not (isFull(bookingQueue)):
        bg_image = ImageTk.PhotoImage(Image.open("C:\\Users\\rubys\\Downloads\\pinterest.png"))

        # -- WELCOME WINDOW --
        # Background Image
        background_label = tk.Label(root, image=bg_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Welcome Label
        welcome_label = tk.Label(root, text='Welcome to BookMySalon!', bg='#FFC0CB', font=('Helvetica', 26, 'bold'))
        welcome_label.pack(pady=10)
        root.config(bg='#FFE0E0')
        description_label = tk.Label(root, text='BookMySalon is your one-stop destination for all your beauty needs! ',
                                     bg='#FFC0CB', font=('Arial', 13))
        description_label.pack(pady=10)

        booking_frame = tk.Frame(root, bg='#FEE8F5')
        booking_frame.pack(pady=20)

        # Booking Appointment
        booking_label = tk.Label(booking_frame, text='If you want to book an appointment, click the button below:',
                                 bg='#FEE8F5')
        booking_label.pack()

        book_button = tk.Button(booking_frame, text='Book Appointment', bg='#FFCCE5', command=bookingaptwindow)
        book_button.pack(pady=10)

        # Cancelling Appointment
        cancel_label = tk.Label(booking_frame, text='If you want to cancel an appointment, click the button below',
                                bg='#FEE8F5')
        cancel_label.pack()

        cancel_button = tk.Button(booking_frame, text='Cancel Appointment', bg='#FFCCE5', command=cancelapt)
        cancel_button.pack(pady=10)

        root.mainloop()


root = tk.Tk()
root.geometry('600x600')
root.title('BookMySalon')
final()