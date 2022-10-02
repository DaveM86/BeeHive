'''
This Application connects a Postgresql database named equiptment to act as the GUI for that database.
'''
from tkinter import ttk
import tkinter as tk
import os
from mailmerge import MailMerge
from ttkthemes import ThemedTk
import psycopg2 as pg2
from win32com import client
import chart_studio.plotly as py
import plotly.graph_objs as go 
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import pandas as pd
import webbrowser

serial_number = ''



def combine_funcs(*funcs):
    '''
    General function used to split two arguments provided by a button click.
    '''
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func



def get_connected():
    def set_connection():
        password = entry_pass.get()
        try:
            conn = pg2.connect(database='Assets', user='postgres', password=password)
            connection = Data_Connection(password=password)
            print('Connected to Database')
            conn.close()
            root.destroy()
            main(connection)
        except:
            print('Incorrect Password')
            entry_pass.delete(0,tk.END)
    
    root = tk.Tk()   
    root.title('Connect')
    canvas4 = tk.Canvas(root, width=275, height=125)
    canvas4.pack()

    fr1_4 = ttk.Frame(root)
    fr1_4.place(relx=0, rely=0, relwidth=1, relheight=1)

    fr1_5 = ttk.Frame(fr1_4)
    fr1_5.place(relx=0, rely=0, relwidth=1, relheight=0.6)
    lb_pass = ttk.Label(fr1_5, text = f'Database Password:', anchor = 'sw')
    lb_pass.place(relx=0.05, rely=0.0, relwidth=1, relheight=0.6)
    entry_pass = ttk.Entry(fr1_5, font=('Segoe UI', 10), show="*")
    entry_pass.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

    fr1_6 = ttk.Frame(fr1_4)
    fr1_6.place(relx=0.35, rely=0.7, relwidth=0.4, relheight=0.25)
    connect_but = ttk.Button(fr1_6, text='Connect', command=combine_funcs(set_connection))
    connect_but.place(relx=0, rely=0, relwidth=1, relheight=1)
       
    root.mainloop()  

class Data_Connection():
    
    def __init__(self, password):
        self.password = password


    def query(self, question):
        conn = pg2.connect(database='Assets', user='postgres', password=self.password)
        cur = conn.cursor()
        cur.execute(question)
        return cur.fetchall()
        conn.close()

    def update(self, change, serial_number):
        conn = pg2.connect(database='Assets', user='postgres', password=self.password)
        cur = conn.cursor()
        cur.execute(change)
        conn.commit()
        if 'DELETE' in change:
        	activity_type = 'Deletion'
        if 'UPDATE' in change:
        	activity_type = 'Amendment'
        if 'INSERT' in change:
        	activity_type = 'New Asset'
        cur.execute('''INSERT INTO activity_log(activity_type, serial_number, query_submitted) VALUES(%s, %s, %s);''', (activity_type, serial_number, change))
        conn.commit()
        conn.close()

    def update_comments(self, change):
        conn = pg2.connect(database='Assets', user='postgres', password=self.password)
        cur = conn.cursor()
        cur.execute(change)
        conn.commit()

    def serial_to_location(self, serial_number):
        try:
            conn = pg2.connect(database='Assets', user='postgres', password=self.password)
            try:
                cur = conn.cursor()
                cur.execute('''SELECT building_capability FROM location INNER JOIN equiptment \
                	on location.location_id = equiptment.location_id WHERE serial_number = %s''', (serial_number,))
                conn.close()
            except:
                print('Nothing could be found with this serial number')        
        except:
            print('No connection to Database')
    
    def paperwork_731(self, serial_number):
        try:
            conn = pg2.connect(database='Assets', user='postgres', password=self.password)
            try:
                cur = conn.cursor()
                cur.execute('''SELECT part_number, description FROM equiptment WHERE serial_number = %s''', (serial_number,))
                return (cur.fetchone())
                conn.close()
            except:
                print('Nothing could be found with this serial number')        
        except:
            print('No connection to Database')

    def export_CSV(self, report_format):
        conn = pg2.connect(database='Assets', user='postgres', password=self.password)
        cur = conn.cursor()
        cur.execute(report_format)

def main(connection):
    serial_number = ''
    '''
    Setting the look and feel off the main page and the widgets that will be perminatly on screen within the application.
    '''
    def set_data():
        '''
        Sets the list options on the main application page by querying the database for erial_number and description
        '''
        list_box_bottom.delete(0, tk.END)
        question = ('''SELECT serial_number, description FROM equiptment ORDER BY description''')
        response = connection.query(question)
        for serial_number, description in response:
            list_box_bottom.insert(tk.END, f'{serial_number}  {description}')

    def get_database():
        '''
        Filters the data show in the list box by entry provided from the user,
        uses the AND and OR opertors to allow flexible searching of the database.
        '''
        filt = entry_filter.get()
        if filt == None:
            list_box_bottom.delete(0, tk.END)
            question = ('''SELECT serial_number, description FROM equiptment ORDER BY description''')
            response = connection.query(question)
            for serial_number, description in response:
                list_box_bottom.insert(tk.END, f'{serial_number} {description}')

        elif ' AND ' in filt:
            head, sep, tail = filt.partition(' AND ')
            q_1 = '%'+head+'%'
            q_2 = '%'+tail+'%'
            list_box_bottom.delete(0, tk.END)
            question = f'''SELECT serial_number, description FROM equiptment \
                INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id \
                WHERE (description ILIKE '{q_1}' or serial_number ILIKE '{q_1}' \
                or location.building_capability ILIKE '{q_1}' or part_number ILIKE '{q_1}' \
                or room_box.room_box ILIKE '{q_1}') AND (description ILIKE '{q_2}' \
                or serial_number ILIKE '{q_2}' or location.building_capability ILIKE '{q_2}' \
                or part_number ILIKE '{q_2}' or room_box.room_box ILIKE '{q_2}') ORDER BY description;'''
            response = connection.query(question)
            for serial_number, description in response:
                list_box_bottom.insert(tk.END, f'{serial_number} {description}')

        elif ' OR ' in filt:
            head, sep, tail = filt.partition(' AND ')
            q_1 = '%'+head+'%'
            q_2 = '%'+tail+'%'
            list_box_bottom.delete(0, tk.END)
            question = f'''SELECT serial_number, description FROM equiptment \
                INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id \
                WHERE (description ILIKE '{q_1}' or serial_number ILIKE '{q_1}' \
                or location.building_capability ILIKE '{q_1}' or part_number ILIKE '{q_1}' \
                or room_box.room_box ILIKE '{q_1}') OR (description ILIKE '{q_2}' \
                or serial_number ILIKE '{q_2}' or location.building_capability ILIKE '{q_2}' \
                or part_number ILIKE '{q_2}' or room_box.room_box ILIKE '{q_2}') ORDER BY description;'''
            response = connection.query(question)
            for serial_number, description in response:
                list_box_bottom.insert(tk.END, f'{serial_number} {description}')

        else:
            q_1 = '%'+filt+'%'
            list_box_bottom.delete(0, tk.END)
            question = f'''SELECT serial_number, description FROM equiptment \
                INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id \
                WHERE (description ILIKE '{q_1}' or serial_number ILIKE '{q_1}' \
                or location.building_capability ILIKE '{q_1}' or part_number ILIKE '{q_1}' \
                or room_box.room_box ILIKE '{q_1}' or barcode ILIKE '{q_1}')'''
            response = connection.query(question)
            for serial_number, description in response:
                list_box_bottom.insert(tk.END, f'{serial_number} {description}')

    def activity_log():

        def display_information():
            display_listbox_choice = display_listbox.curselection()[0]
            choice = display_listbox.get(display_listbox_choice)[0:14]
            question = (f"SELECT datetime, serial_number, activity_type, query_submitted FROM activity WHERE datetime = '{choice}';")
            response = connection.query(question)
            for information in response:
            	information_to_display = tk.StringVar()
            	information_to_display.set('Date Time: '+information[0]+'\n'+'\n'+'Asset Serial Number: '+information[1]+'\n'+'\n'+'Activity Type: '+information[2]+'\n'+'\n'+'Query:'+'\n'+information[3])
            	print_information.delete('1.0', tk.END)
            	print_information.insert("1.0", information_to_display.get())

        def filter_listbox():
            
            filt_text = search_entry.get()
            filt_days = days_entry.get()

            if filt_text == '' and filt_days == '':
                question = (f'SELECT datetime, activity_type, serial_number FROM activity ORDER BY datetime DESC')
                response = connection.query(question)
                print(response)
                display_listbox.delete(0, tk.END)
                for activity in response:
                    datetime = activity[0]
                    activity_type = activity[1]
                    serial_number = activity[2]
                    display_listbox.insert(tk.END,f'{datetime} {activity_type} {serial_number}')
        
            elif filt_text != '' and filt_days == '':
                question = (f"SELECT datetime, activity_type, serial_number FROM activity \
                    WHERE activity_type = '{filt_text}' or serial_number = '{filt_text}' ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for activity in response:
                    datetime = activity[0]
                    activity_type = activity[1]
                    serial_number = activity[2]
                    display_listbox.insert(tk.END,f'{datetime} {activity_type} {serial_number}')
            
            elif filt_text == '' and filt_days != '':
                question = (f"SELECT TO_CHAR(date_time, 'dd-mm-yy HH24:MI') as datetime, activity_type, \
                	serial_number FROM activity_log WHERE date_time > ((CURRENT_TIMESTAMP) - interval '{filt_days} days') ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for activity in response:
                    datetime = activity[0]
                    activity_type = activity[1]
                    serial_number = activity[2]
                    display_listbox.insert(tk.END,f'{datetime} {activity_type} {serial_number}')

            elif filt_text != '' and filt_days != '':
                question = (f"SELECT TO_CHAR(date_time, 'dd-mm-yy HH24:MI') as datetime, activity_type, \
                	serial_number FROM activity_log WHERE (date_time > ((CURRENT_TIMESTAMP) - interval '{filt_days} days')) \
                	AND (activity_type = '{filt_text}' or serial_number = '{filt_text}') ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for activity in response:
                    datetime = activity[0]
                    activity_type = activity[1]
                    serial_number = activity[2]
                    display_listbox.insert(tk.END,f'{datetime} {activity_type} {serial_number}')

        activity_log = tk.Toplevel(width=700, height=350)
        activity_log.title('Activity Log')

        canvas = tk.Canvas(activity_log)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)


        selection_frame = tk.Frame(activity_log)
        selection_frame.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        information_frame = tk.Frame(activity_log)
        information_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        title_lable = tk.Label(selection_frame, text='Activity Log', font=('Segoe UI', 12, 'bold'), anchor='nw')
        title_lable.place(relx=0.05, rely=0.05, relwidth=0.95, relheight=0.1)
        
        filt_label = tk.Label(selection_frame, text='Show results for how many days?:', font=('Segoe UI', 10), anchor='w')
        filt_label.place(relx=0.05, rely=0.15, relwidth=0.75, relheight=0.07)        
        
        days_entry = ttk.Entry(selection_frame)
        days_entry.place(relx=0.8, rely=0.15, relwidth=0.2, relheight=0.07)
        
        search_entry = ttk.Entry(selection_frame)
        search_entry.place(relx=0.05, rely=0.23, relwidth=0.6, relheight=0.07)
        
        search_button = ttk.Button(selection_frame, text='Search', command=filter_listbox)
        search_button.place(relx=0.65, rely=0.23, relwidth=0.35, relheight=0.07)        

        display_listbox = tk.Listbox(selection_frame)
        display_listbox.bind("<<ListboxSelect>>", lambda x: display_information())
        display_listbox.place(relx=0.05, rely=0.32, relwidth=0.95, relheight=0.63)

        question = (f'SELECT datetime, activity_type, serial_number FROM activity ORDER BY datetime DESC')
        response = connection.query(question)
        for activity in response:
            datetime = activity[0]
            activity_type = activity[1]
            serial_number = activity[2]
            display_listbox.insert(tk.END,f'{datetime} {activity_type} {serial_number}')

        print_information = tk.Text(information_frame, font=('Segoe UI', 10))
        print_information.place(relx=0.05, rely=0.32, relwidth=0.90, relheight=0.63)


    def comments_log():
        global serial_number

        def display_information():
            display_listbox_choice = display_listbox.curselection()[0]
            choice = display_listbox.get(display_listbox_choice)[0:14]
            question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number, comment FROM comments \
            	INNER JOIN equiptment on comments.equip_id = equiptment.equip_id \
            	WHERE TO_CHAR(date, 'dd-mm-yy HH24:mi') = '{choice}';")
            response = connection.query(question)
            for information in response:
            	information_to_display = tk.StringVar()
            	information_to_display.set('Date/Time: '+information[0]+'\n'+'\n'+'Asset Serial: '+information[1]+'\n'+'\n'+'Comment:'+'\n'+information[2])
            	print_information.delete('1.0', tk.END)
            	print_information.insert("1.0", information_to_display.get())

        def filter_listbox():
            
            filt_text = search_entry.get()
            filt_days = days_entry.get()

            if filt_text == '' and filt_days == '':
                question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number FROM comments \
                    INNER JOIN equiptment on comments.equip_id = equiptment.equip_id WHERE equiptment.serial_number = '{serial_number}' \
                    ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for comments in response:
                    display_listbox.insert(tk.END,f'{comments[0]} {comments[1]}')
        
            elif filt_text != '' and filt_days == '':
                question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number, comment FROM comments \
                	INNER JOIN equiptment on comments.equip_id = equiptment.equip_id WHERE serial_number = '{serial_number}' AND comment ILIKE '%{filt_text}%' \
                	ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for comments in response:
                    display_listbox.insert(tk.END,f'{comments[0]} {comments[1]}')
            
            elif filt_text == '' and filt_days != '':
                question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number FROM comments \
                    INNER JOIN equiptment on comments.equip_id = equiptment.equip_id WHERE equiptment.serial_number = '{serial_number}'  AND (date > ((CURRENT_TIMESTAMP) - interval '{filt_days} days')) \
                    ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for comments in response:
                    display_listbox.insert(tk.END,f'{comments[0]} {comments[1]}')

            elif filt_text != '' and filt_days != '':
                question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number FROM comments \
                    INNER JOIN equiptment on comments.equip_id = equiptment.equip_id WHERE date > ((CURRENT_TIMESTAMP) - interval '{filt_days} days') \
                    AND serial_number = '{serial_number}' AND comment ILIKE '%{filt_text}%' ORDER BY datetime DESC;")
                response = connection.query(question)
                display_listbox.delete(0, tk.END)
                for comments in response:
                    display_listbox.insert(tk.END,f'{comments[0]} {comments[1]}')

        comments_log = tk.Toplevel(width=700, height=350)
        comments_log.title('Comments')

        canvas = tk.Canvas(comments_log)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)


        selection_frame = tk.Frame(comments_log)
        selection_frame.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        information_frame = tk.Frame(comments_log)
        information_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        title_lable = tk.Label(selection_frame, text='Comments', font=('Segoe UI', 12, 'bold'), anchor='nw')
        title_lable.place(relx=0.05, rely=0.05, relwidth=0.95, relheight=0.1)
        
        filt_label = tk.Label(selection_frame, text='Show results for how many days?:', font=('Segoe UI', 10), anchor='w')
        filt_label.place(relx=0.05, rely=0.15, relwidth=0.75, relheight=0.07)        
        
        days_entry = ttk.Entry(selection_frame)
        days_entry.place(relx=0.8, rely=0.15, relwidth=0.2, relheight=0.07)
        
        search_entry = ttk.Entry(selection_frame)
        search_entry.place(relx=0.05, rely=0.23, relwidth=0.6, relheight=0.07)
        
        search_button = ttk.Button(selection_frame, text='Search', command=filter_listbox)
        search_button.place(relx=0.65, rely=0.23, relwidth=0.35, relheight=0.07)        

        display_listbox = tk.Listbox(selection_frame)
        display_listbox.bind("<<ListboxSelect>>", lambda x: display_information())
        display_listbox.place(relx=0.05, rely=0.32, relwidth=0.95, relheight=0.63)

        question = (f"SELECT TO_CHAR(date, 'dd-mm-yy HH24:mi') as datetime, equiptment.serial_number FROM comments \
            INNER JOIN equiptment on comments.equip_id = equiptment.equip_id WHERE equiptment.serial_number = '{serial_number}' \
            ORDER BY datetime DESC;")
        response = connection.query(question)
        for comments in response:
            display_listbox.insert(tk.END,f'{comments[0]} {comments[1]}')

        print_information = tk.Text(information_frame, font=('Segoe UI', 10))
        print_information.place(relx=0.05, rely=0.32, relwidth=0.90, relheight=0.63)

    def details_comments():
        '''
        This insets the details and comments frame onto the main page of the application
        this is done seperatly to provide options and flexibility on the main page,
        it also allow the user to append comments to the selected asset by passing the entry to add_comment.
        '''
        def add_comment():
            '''
            Add the comment entered by the user to the table comments, as a new row.
            '''
            
            try:
                global serial_number
                question = f'''SELECT equip_id from equiptment WHERE serial_number = '{serial_number}';'''
                response = connection.query(question)
                for equip_id in response:
                    equip_id = response[0][0]
                    comments = entry_comms.get()
                    change = f'''INSERT INTO comments (equip_id, comment) VALUES ({equip_id}, '{comments}')'''
                    print(equip_id)
                    connection.update_comments(change)
                    entry_comms.delete(0,tk.END)
                    label_top_right['text'] = f'Comments have been add to Asset {serial_number}.'
            except:
                label_top_right['text'] = 'Error - Comments could not be add at this time.'


        global label_middle, label_right_bottom_com, label_right_bottom_date, entry_comms
        upper_frame_left = tk.Frame (root)
        upper_frame_left.place(relx=0.45, rely=0.065, relwidth=0.25, relheight=0.85)

        label_middle_top = tk.Label(upper_frame_left, text='Asset Information:', font=('Segoe UI', 12, 'bold'), anchor= 'nw')
        label_middle_top.place(relx=0.03, rely = 0, relwidth=1, relheight=0.05)

        label_middle = tk.Label(upper_frame_left, anchor='nw', font=('Segoe UI', 12), justify='left')
        label_middle.place(relx=0.03, rely=0.05, relwidth=1, relheight=0.3)

        label_right_bottom = tk.Label(upper_frame_left, text='Last Comment:', font=('Segoe UI', 10, 'bold'), anchor='nw', justify='left')
        label_right_bottom.place(relx=0.03, rely=0.3, relwidth=1, relheight=0.05)
        label_right_bottom_date = tk.Label(upper_frame_left, font=('Segoe UI', 8), anchor='nw', justify='left')
        label_right_bottom_date.place(relx=0.03, rely = 0.35, relwidth=1, relheight=0.05)
        label_right_bottom_com = tk.Label(upper_frame_left, font=('Segoe UI', 10), anchor='nw', justify='left')
        label_right_bottom_com.place(relx=0.03, rely=0.4, relwidth=1, relheight=0.35)

        fr_com_1 = tk.Frame(upper_frame_left)
        fr_com_1.place(relx=0.03, rely=0.75, relwidth=1, relheight=0.15)
        entry_comms = ttk.Entry(fr_com_1)
        entry_comms.place(relx=0.03, rely=0, relwidth=0.9, relheight=0.4)
        comms_add_b1 = ttk.Button(fr_com_1, text='Append Comments', command=add_comment)
        comms_add_b1.place(relx=0.03, rely=0.52, relwidth=0.5, relheight=0.4)

    def display_asset():
        '''
        This function querys the database based on the selection made in the list box for further information
        this is passed to the format_response funtion to process it is displayed with the details and comments frame
        '''
        global serial_number
        try:
            list_box_choice = list_box_bottom.curselection()[0]
            choice = list_box_bottom.get(list_box_choice)
            serial_number = choice.split(' ')[0]
            question = f'''SELECT equiptment.serial_number, equiptment.description, \
                equiptment.part_number, location.building_capability, room_box.room_box \
                FROM equiptment INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id \
                WHERE serial_number ='{serial_number}';'''
            response = connection.query(question)
            label_middle['text'] = format_response(response)

            label_right_bottom_com['text'] = ''
            label_right_bottom_date['text'] = ''
            question = f'''SELECT TO_CHAR(date, 'dd-mm-yyyy HH24:MI'), comment FROM comments \n
                INNER JOIN equiptment on comments.equip_id = equiptment.equip_id \n
                WHERE equiptment.serial_number = '{serial_number}' ORDER BY comments.date DESC LIMIT(1)'''
            response = connection.query(question)
            label_right_bottom_com['text'] = format_response_com(response)
        except:
        	print('display asset error')

    def format_response(response):
        '''
        formats the information passed by display_asset
        '''
        final_str = ''
        try:
            for serial, desc, part_no, location, room_box in response:
                final_str = (f'Description:\t {desc}'+'\n'f'Serial Number:\t {serial}'+'\n'f'Part Number:\t {part_no}'+'\n'f'Site Location:\t {location}'+'\n'f'Room or Box:\t {room_box}')
        except:
            final_str = ("sorry that can't be found")

        return final_str

    def format_response_com(last_comment):
        '''
        Attempts to format the last comment in the database for the specified asset.
        '''
        try:
            for date, comment in last_comment:
                label_right_bottom_date['text'] = date
                comment = comment
                final_li = []
                final_str= ''
                space=0
                for i in comment:
                    final_li.append(i)
                    if(i.isspace()):
                        space=space+1
                        if space % 5 == 0:
                            final_li.append('\n')
                            if space > 30:
                                final_li.append('....use all comments tab to see more')
                                break

            final_str = ''.join(final_li)
            return final_str
        except:
            final_str = ''
            return final_str



    def gen_731():
        '''
        generates a pop out window to recieve the detals of the 731 paperwork to be printed
        '''
        def print_731():
            '''
            This uses the mailmerge module to add details to a word template and save the created document in the same directory
            it then opns that directory.
            '''
            global serial_number

            Cpl = entry_cpl.get()
            last_power = entry_lastpow.get()
            snow = entry_snow.get()
            date_731 = entry_date.get()

            response = connection.paperwork_731(serial_number)
            part_number = response[0]
            description = response[1]

            os.chdir("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work")
            template = "731_Do_Not_Delete.docx"
            document = MailMerge(template)
            field_name = (document.get_merge_fields())
            document.merge(a=snow[0], b=snow[1], c=snow[2], d=snow[3], e=snow[4], f=snow[5], g=snow[6], h=snow[7], i=snow[8], \
                j=snow[9], k=snow[10], l=snow[11], m=snow[12], n=snow[13], o=snow[14], Part_NO=part_number, Serial_NO=serial_number, \
                Desc=description, Last_Power=last_power, Cpl=Cpl, Date=date_731)

            word = client.DispatchEx("Word.Application")
            
            document.write('731_'+serial_number+'.docx')
            
            doc = word.Documents.Open("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work\\"+'731_'+serial_number+'.docx')
            doc.SaveAs("C:\\Users\\Dmacm\\Desktop\\Asset Management\\731 Docs\\"+'731_'+serial_number+'.pdf', FileFormat=17)
            doc.Close()
            
            os.remove("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work\\"+'731_'+serial_number+'.docx')
            
            path = "C:\\Users\\Dmacm\\Desktop\\Asset Management\\731 Docs"
            path = os.path.realpath(path)
            os.startfile(path)       
            label_top_right['text'] = f'LAST ACTION - 731 Generated for Asset {serial_number}.'


        global serial_number 

        top = tk.Toplevel()
        top.title('Generate 731')
        canvas2 = tk.Canvas(top, width=300, height=450)
        canvas2.pack()
        fr1 = ttk.Frame(top)
        fr1.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        label_gen_731_header = tk.Label(fr1, text='Generate 731', font=('Segoe UI', 12, 'bold'), anchor= 'sw')
        label_gen_731_header.place(relx=0.05, rely = 0.03, relwidth=0.9, relheight=0.05)

        fr2 = ttk.Frame(fr1)
        fr2.place(relx=0, rely=0.11, relwidth=1, relheight=0.15)	
        lb_snow = ttk.Label(fr2, text = 'Please enter the Snow/ACNO/Date\nRaised in format 1164MISC1241220:', anchor='sw')
        lb_snow.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_snow = ttk.Entry(fr2)
        entry_snow.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr3 = ttk.Frame(fr1)
        fr3.place(relx=0, rely=0.28, relwidth=1, relheight=0.15)
        lastpow = ttk.Label(fr3, text='Please enter any remarks:', anchor='sw')
        lastpow.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_lastpow = ttk.Entry(fr3)
        entry_lastpow.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr4 = ttk.Frame(fr1)
        fr4.place(relx=0, rely=0.45, relwidth=1, relheight=0.15)
        lb3_cpl = ttk.Label(fr4, text='Please enter Rank and Name\nof supervisor signing 731:', anchor='sw')
        lb3_cpl.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_cpl = ttk.Entry(fr4)
        entry_cpl.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr5 = ttk.Frame(fr1)
        fr5.place(relx=0, rely=0.62, relwidth=1, relheight=0.15)
        lb4_date = ttk.Label(fr5, text='Please enter the date of signing,\nleave blank if unknown:', anchor='sw')
        lb4_date.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_date = ttk.Entry(fr5)
        entry_date.place(relx=0.05, rely=0.6, relwidth=0.90, relheight=0.4)

        print_b1 = ttk.Button(fr1, text='Print731', command = print_731)
        print_b1.place(relx=0.3, rely=0.85, relwidth=0.4, relheight=0.10)

    def bulk_gen_731():
        '''
        this pops out the form for the mass generation of 731's
        '''
        def bulk_print_731():

            Cpl = entry_cpl.get()
            last_power = entry_lastpow.get()
            snow = entry_snow.get()
            date_731 = entry_date.get()
            filt = entry_cap.get()

            question = f'''SELECT serial_number, part_number, description FROM equiptment \
                INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id \
                WHERE (description ILIKE '{filt}' or serial_number ILIKE  '{filt}' \
                or location.building_capability ILIKE '{filt}' or part_number ILIKE '{filt}' \
                or room_box.room_box ILIKE '{filt}') ORDER BY description;'''
            response = connection.query(question)

            for assets in response:
                serial_number = assets[0]
                part_number = assets[1]
                description = assets[2]

                os.chdir("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work")
                template = "731_Do_Not_Delete.docx"
                document = MailMerge(template)
                field_name = (document.get_merge_fields())
                document.merge(a=snow[0], b=snow[1], c=snow[2], d=snow[3], e=snow[4], f=snow[5], g=snow[6], h=snow[7], i=snow[8], \
                    j=snow[9], k=snow[10], l=snow[11], m=snow[12], n=snow[13], o=snow[14], Part_NO=part_number, Serial_NO=serial_number, \
                    Desc=description, Last_Power=last_power, Cpl=Cpl, Date=date_731)
            
                word = client.DispatchEx("Word.Application")
            
                document.write('731_'+serial_number+'.docx')
            
                doc = word.Documents.Open("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work\\"+'731_'+serial_number+'.docx')
                doc.SaveAs("C:\\Users\\Dmacm\\Desktop\\Asset Management\\731 Docs\\"+'731_'+serial_number+'.pdf', FileFormat=17)
                doc.Close()
            
                os.remove("C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work\\"+'731_'+serial_number+'.docx')


            path = "C:\\Users\\Dmacm\\Desktop\\Asset Management\\731 Docs"
            path = os.path.realpath(path)
            os.startfile(path)


        top = tk.Toplevel()
        top.title('Bulk Generate 731')
        canvas2 = tk.Canvas(top, width=300, height=450)
        canvas2.pack()
        fr1 = ttk.Frame(top)
        fr1.place(relx=0, rely=0, relwidth=1, relheight=1)

        fr_cap = ttk.Frame(fr1)
        fr_cap.place(relx=0, rely=0, relwidth=1, relheight=0.15)	
        lb_cap = ttk.Label(fr_cap, text = 'Please enter the filter for the bulk\ngeneration of 731s e.g. Capability 1', anchor='sw')
        lb_cap.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_cap = ttk.Entry(fr_cap)
        entry_cap.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr2 = ttk.Frame(fr1)
        fr2.place(relx=0, rely=0.166, relwidth=1, relheight=0.15)	
        lb_snow = ttk.Label(fr2, text='Please enter the Snow/ACNO/Date\nRaised in format 1164MISC1241220:', anchor='sw')
        lb_snow.place(relx=0.05, rely=0, relwidth=0.9, relheight=0.6)
        entry_snow = ttk.Entry(fr2)
        entry_snow.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr3 = ttk.Frame(fr1)
        fr3.place(relx=0, rely=0.332, relwidth=1, relheight=0.15)
        lastpow = ttk.Label(fr3, text='Please enter any remarks:', anchor='sw')
        lastpow.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_lastpow = ttk.Entry(fr3)
        entry_lastpow.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr4 = ttk.Frame(fr1)
        fr4.place(relx=0, rely=0.498, relwidth=1, relheight=0.15)
        lb3_cpl = ttk.Label(fr4, text='Please enter Rank and Name\nof supervisor signing 731:', anchor='sw')
        lb3_cpl.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_cpl = ttk.Entry(fr4)
        entry_cpl.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        fr5 = ttk.Frame(fr1)
        fr5.place(relx=0, rely=0.664, relwidth=1, relheight=0.15)
        lb4_date = ttk.Label(fr5, text='Please enter the date of signing,\nleave blank if unknown:', anchor='sw')
        lb4_date.place(relx=0.05, rely=0.0, relwidth=0.9, relheight=0.6)
        entry_date = ttk.Entry(fr5)
        entry_date.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.4)

        print_b1 = ttk.Button(fr1, text='Print 731', command=bulk_print_731)
        print_b1.place(relx=0.3, rely=0.88, relwidth=0.4, relheight=0.10)


    def update_asset():
        '''
        sets the pane for the update of an asset within thedatabase
        '''
        
        global serial_number
        
        update_loc = []
        desc = ''
        part_no = ''

        def reenable_selection():
            '''
            Reenables the ue of the selection list box that was supended whilst update asset was in use.
            '''
            list_box_bottom['state'] = 'normal'

        def reset_update_form():
            '''
            This resets the default vaules of the update asset form to blank.
            '''
            entry_update_serial['state'] = 'active'
            entry_update_serial.delete(0,tk.END)
            entry_update_serial['state'] = 'disabled'
            entry_update_part.delete(0,tk.END)
            entry_update_desc.delete(0,tk.END)        
        
        def pick_room(e):
            '''
            creates cascading filters on the drop down boxes so only rooms within the selected building can be chosen.
            '''
            update_room_menu.config(value=[])
            update_room = []
            sel_loc = update_loc_menu.get()
            question = f'''SELECT room_box from room_box INNER JOIN location ON room_box.location_id = location.location_id WHERE location.building_capability LIKE '{sel_loc}';'''
            response = connection.query(question)
            for room in response:
                update_room.append(room[0])
            update_room_menu.config(value=update_room)
        

        def update_asset_complete():
            '''
            inaserts the new asset into the data base
            '''
            serial_number = entry_update_serial.get()
            part_number = entry_update_part.get()
            desc = entry_update_desc.get()
            location = update_loc_menu.get()
            room = update_room_menu.get()

            if serial_number == '' or part_number == '' or desc == '':
                label_top_right['text'] = 'Error - Please ensure that all fields are populate when updating an asset.'

            else:
                try:
                    question = f'''SELECT location_id FROM location WHERE building_capability = '{location}';'''
                    response = connection.query(question)
                    location = response[0][0]

                    question = f'''SELECT room_box_id FROM room_box WHERE room_box = '{room}';'''
                    response = connection.query(question)
                    room = response[0][0]

                except:
                    label_top_right['text'] = 'Error - Please ensure that all fields are populate when updating an asset.'


                try:
                    change = f'''UPDATE equiptment SET  part_number = '{part_number}', description = '{desc}', location_id = {location}, room_box_id = {room} WHERE serial_number = '{serial_number}'; '''
                    connection.update(change, serial_number)
                    label_top_right['text'] = f'LAST ACTION - Asset {serial_number} details updated within database.'
                except:
                    label_top_right['text'] = 'Error - please check all fields are populated correctly and try again.'
            

        question = f'''SELECT description, part_number FROM equiptment WHERE serial_number = '{serial_number}';'''
        response = connection.query(question)

        for description, part_number in response:
            desc = description
            part_no = part_number

        update_asset_frame = tk.Frame (root)
        update_asset_frame.place(relx=0.75, rely=0.065, relwidth=0.25, relheight=0.85)
        
        #serialnumber
        label_update_header = tk.Label(update_asset_frame, text='Update Asset', font=('Segoe UI', 12, 'bold'), anchor= 'nw')
        label_update_header.place(relx=0, rely = 0, relwidth=0.9, relheight=0.05)
        label_update_serial = tk.Label(update_asset_frame, text='Serial_NO:', state = 'disabled', font=('Segoe UI', 10), anchor='sw')
        label_update_serial.place(relx=0, rely=0.05, relwidth=0.9, relheight=0.06)
        
        #entry_update_serial
        entry_update_serial = ttk.Entry(update_asset_frame)
        entry_update_serial.place(relx=0, rely=0.11, relwidth=0.9, relheight=0.06)
        entry_update_serial.insert(0,serial_number)
        entry_update_serial['state'] = 'disabled'
        
        #part_number
        label_update_part = tk.Label(update_asset_frame, text='Update Part_NO:', font=('Segoe UI', 10), anchor='sw')
        label_update_part.place(relx=0, rely=0.17, relwidth=0.9, relheight=0.06)
        
        #entry_update_part
        entry_update_part = ttk.Entry(update_asset_frame)
        entry_update_part.place(relx=0, rely=0.23, relwidth=0.9, relheight=0.06)
        entry_update_part.insert(0,part_no)
        
        #description
        label_update_desc = tk.Label(update_asset_frame, text='Update Asset Description:', font=('Segoe UI', 10), anchor='sw')
        label_update_desc.place(relx=0, rely=0.29, relwidth=0.9, relheight=0.06)
        
        #entry_update_desc
        entry_update_desc = ttk.Entry(update_asset_frame)
        entry_update_desc.place(relx=0, rely=0.35, relwidth=0.9, relheight=0.06)
        entry_update_desc.insert(0,desc)
        
        #location
        label_update_loc = tk.Label(update_asset_frame, text='Update Location:', font=('Segoe UI', 10), anchor='sw')
        label_update_loc.place(relx=0, rely=0.41, relwidth=0.9, relheight=0.06)
        
        #entry_update_location
        question = ('''SELECT building_capability from location;''')
        response = connection.query(question)
        
        for building_capability in response:
            update_loc.append(building_capability[0])
        
        update_loc_menu = ttk.Combobox(update_asset_frame, value=update_loc)
        update_loc_menu.place(relx=0, rely=0.47)
        update_loc_menu.bind('<<ComboboxSelected>>', pick_room)

        #room_box
        label_update_room = tk.Label(update_asset_frame, text='Update Room:', font=('Segoe UI', 10), anchor='sw')
        label_update_room.place(relx=0, rely=0.52, relwidth=0.9, relheight=0.06) 
        
        #entry_update_room
        update_room_menu = ttk.Combobox(update_asset_frame, value=[' '])
        update_room_menu.place(relx=0, rely=0.58)

        update_bu_1 = ttk.Button(update_asset_frame, text='Commit Changes', command=combine_funcs(update_asset_complete, reenable_selection, reset_update_form))
        update_bu_1.place(relx=0, rely=0.83, relwidth=0.4, relheight=0.06)
        update_bu_2 = ttk.Button(update_asset_frame, text='Clear', command=combine_funcs(reset_update_form, reenable_selection))
        update_bu_2.place(relx=0.5, rely=0.83, relwidth=0.4, relheight=0.06)

    def disable_selection():
        '''
        disables the use of the selection list box whilst the update asset function is in use.
        '''
        list_box_bottom['state']='disabled'
    
    def add_asset():
        '''
        sets the pane for the addiion of an asset to the database
        '''
        add_loc = []

        def create_asset():
            '''
            inaserts the new asset into the data base
            '''
            serial_number = entry_add_serial.get()
            part_number = entry_add_part.get()
            desc = entry_add_desc.get()
            barcode = entry_add_barcode.get()
            location = add_loc_menu.get()
            room = add_room_menu.get()

            if serial_number == '' or part_number == '' or desc == '':
                label_top_right['text'] = 'Error - Please ensure that all required fields are populate when adding an asset.'

            else:
                try:
                    question = f'''SELECT location_id FROM location WHERE building_capability = '{location}';'''
                    response = connection.query(question)
                    location = response[0][0]
                    print(location)

                    question = f'''SELECT room_box_id FROM room_box WHERE room_box = '{room}';'''
                    response = connection.query(question)
                    room = response[0][0]
                    print(room)

                except:
                    label_top_right['text'] = 'Error - Please ensure that all fields are populate when adding an asset.'

                try:
                    # find if serial number is destinct
                    question = f'''SELECT serial_number FROM equiptment WHERE serial_number = '{serial_number}';'''
                    response = connection.query(question)
                    serial_distinct = response[0][0]
                    print(serial_distinct)
                    label_top_right['text'] = f'Error - {serial_number} already exists in database.'

                except:
                    print('Serial Number is unique')
                    try:
                        change = f'''INSERT INTO equiptment(serial_number, part_number, description, location_id, room_box_id, barcode) VALUES ('{serial_number}', '{part_number}', '{desc}', '{location}', '{room}', '{barcode}')'''
                        connection.update(change, serial_number)
                        label_top_right['text'] = 'LAST ACTION - Asset added to database.'
                    except:
                        label_top_right['text'] = 'Error - please check all fields are populated correctly and try again.'
        
        def pick_room(e):
            '''
            creates cascading filters on the drop down boxes so only rooms within the selected building can be chosen.
            '''
            add_room_menu.config(value=[])
            add_room = []
            sel_loc = add_loc_menu.get()
            question = f'''SELECT room_box from room_box INNER JOIN location ON room_box.location_id = location.location_id WHERE location.building_capability LIKE '{sel_loc}';'''
            response = connection.query(question)
            for room in response:
                add_room.append(room[0])
            add_room_menu.config(value=add_room)
        
        asset = tk.Toplevel()
        asset.title('Add Asset')
        canvas_asset = tk.Canvas(asset, width=620, height=280)
        canvas_asset.pack()

        add_asset_frame = tk.Frame (asset, bd=4)
        add_asset_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        label_add_header = tk.Label(add_asset_frame, text='Add New Asset', font=('Segoe UI', 12, 'bold'), anchor= 'nw')
        label_add_header.place(relx=0.05, rely = 0, relwidth=0.5, relheight=0.08)            
        #serialnumber
        label_add_serial = tk.Label(add_asset_frame, text='Please Enter Serial_NO:', font=('Segoe UI', 10), anchor='sw')
        label_add_serial.place(relx=0.05, rely=0.08, relwidth=0.40, relheight=0.10)
        #entry_add_serial
        entry_add_serial = ttk.Entry(add_asset_frame)
        entry_add_serial.place(relx=0.05, rely=0.18, relwidth=0.3, relheight=0.10)

        #part_number
        label_add_part = tk.Label(add_asset_frame, text='Please Enter Part_NO:', font=('Segoe UI', 10), anchor='sw')
        label_add_part.place(relx=0.05, rely=0.28, relwidth=0.40, relheight=0.10)
        #entry_add_part
        entry_add_part = ttk.Entry(add_asset_frame)
        entry_add_part.place(relx=0.05, rely=0.38, relwidth=0.3, relheight=0.10)

        #description
        label_add_desc = tk.Label(add_asset_frame, text='Please Enter Asset Description:', font=('Segoe UI', 10), anchor='sw')
        label_add_desc.place(relx=0.05, rely=0.48, relwidth=0.40, relheight=0.10)
        #entry_add_desc
        entry_add_desc = ttk.Entry(add_asset_frame)
        entry_add_desc.place(relx=0.05, rely=0.58, relwidth=0.3, relheight=0.10)

        #location
        label_add_loc = tk.Label(add_asset_frame, text='Please Select Location:', font=('Segoe UI', 10), anchor='sw')
        label_add_loc.place(relx=0.4, rely=0.08, relwidth=0.30, relheight=0.10)
        #entry_add_location
        question = ('''SELECT building_capability from location;''')
        response = connection.query(question)
        for building_capability in response:
            add_loc.append(building_capability[0])
        add_loc_menu = ttk.Combobox(add_asset_frame, value=add_loc)
        add_loc_menu.place(relx=0.4, rely=0.18)
        add_loc_menu.bind('<<ComboboxSelected>>', pick_room)

        #room_box
        label_add_room = tk.Label(add_asset_frame, text='Please Select Room:', font=('Segoe UI', 10), anchor='sw')
        label_add_room.place(relx=0.4, rely=0.28, relwidth=0.30, relheight=0.10) 
        #entry_add_room
        add_room_menu = ttk.Combobox(add_asset_frame, value=[' '])
        add_room_menu.place(relx=0.4, rely=0.38)
        
        #barcode
        label_add_barcode = tk.Label(add_asset_frame, text='Please Scan Allocated Barcode:', font=('Segoe UI', 10), anchor='sw')
        label_add_barcode.place(relx=0.4, rely=0.48, relwidth=0.30, relheight=0.10)
        #entry_add_desc
        entry_add_barcode = ttk.Entry(add_asset_frame)
        entry_add_barcode.place(relx=0.4, rely=0.58, relwidth=0.3, relheight=0.10)

        add_bu_1 = ttk.Button(add_asset_frame, text='Create Asset', command=combine_funcs(create_asset, asset.destroy))
        add_bu_1.place(relx=0.15, rely=0.82, relwidth=0.3, relheight=0.12)
        add_bu_2 = ttk.Button(add_asset_frame, text='Cancel', command=asset.destroy)
        add_bu_2.place(relx=0.55, rely=0.82, relwidth=0.3, relheight=0.12)




    def delete_asset():
        '''
        function to remove asset from the database
        '''
        global serial_number
        def delete_complete():
            '''
            function to commit the removal of the asset from the database
            '''
            try:
                change = f'''DELETE FROM equiptment WHERE serial_number = '{asset_to_delete}';'''
                connection.update(change, asset_to_delete)
                label_top_right['text'] = f'{asset_to_delete} has been removed from the database' 
            except:
                label_top_right['text'] = f'Error - {asset_to_delete} could not be deleted from database.'
        
        asset_to_delete = serial_number
        if asset_to_delete == '':
            label_top_right['text'] = 'Error - please select an asset to remove.'
        else:
            delete = tk.Toplevel()
            delete.title('Connect')
            canvas4 = tk.Canvas(delete, width=275, height=125)
            canvas4.pack()

            frame_delete = ttk.Frame(delete)
            frame_delete.place(relx=0, rely=0, relwidth=1, relheight=1)
            lb_delete = tk.Label(frame_delete, text = f'Deleteing {asset_to_delete}?', font=('Segoe UI', 10))
            lb_delete.place(relx=0.05, rely=0.3, relwidth=0.95, relheight=0.2)
            delete_but = ttk.Button(frame_delete, text='Continue', command=combine_funcs(delete_complete, delete.destroy))
            delete_but.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.3)

    def run_extract_equip():
        report_format = ('''copy (SELECT serial_number, part_number, description, location.building_capability, room_box.room_box FROM equiptment INNER JOIN location ON equiptment.location_id = location.location_id \
                INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id ORDER BY location.building_capability, description) to 'C:/Users/Public/equiptment_data_1.csv' csv header;''')
        connection.export_CSV(report_format)
        os.replace("C:/Users/Public/equiptment_data_1.csv", "C:/Users/Dmacm/Desktop/Asset Management/reports/equiptment_data.csv")
        os.startfile("C:/Users/Dmacm/Desktop/Asset Management/reports/equiptment_data.csv")
    
    def run_extract_network_connections():
        report_format = ('''copy (SELECT switches.switch_serial AS switch_serial, network_connections.port_number, location.building_capability AS switch_loc_building, 
        	room_box.room_box AS switch_loc_room, location_equiptment.serial_number AS connected_equip, location_equiptment.description AS conn_equip_desc, 
        	location_equiptment.building_capability AS connected_equip_location, location_equiptment.room_box AS connected_equip_room 
        	FROM network_connections 
        	INNER JOIN switches on network_connections.switch_id = switches.switch_id 
        	INNER JOIN location on switches.location_id = location.location_id 
        	INNER JOIN (SELECT * from equiptment 
			INNER JOIN location on equiptment.location_id = location.location_id
			INNER JOIN room_box on equiptment.room_box_id = room_box.room_box_id) AS location_equiptment
			on network_connections.equip_id = location_equiptment.equip_id 
			INNER JOIN room_box on switches.room_id = room_box.room_box_id 
			ORDER BY switch_serial) to 'C:/Users/Public/network_connections.csv' csv header;''')
        connection.export_CSV(report_format)
        os.replace("C:/Users/Public/network_connections.csv", "C:/Users/Dmacm/Desktop/Asset Management/reports/network_connections.csv")
        os.startfile("C:/Users/Dmacm/Desktop/Asset Management/reports/network_connections.csv")

#reports and dash boards

    # def deployment_report():
    #     df = pd.read_csv('C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\paper_work\\deployment')
    #     df.head()
    #     data = dict(
    #             type = 'choropleth',
    #             locations = df['deployment_location'],
    #             z = df['num_personnel_req'],
    #             # text = df['COUNTRY'],
    #             colorscale= 'Portland',
    #             colorbar = {'title' : 'Number of Personnel'},
    #             marker = dict(line = dict(color = 'rgb(255,255,255)',width = 1))
    #             )
    #     layout = dict(
    #         title = 'Deployed Locations Next 12 Months',
    #         geo = dict(
    #             showframe = False,
    #             projection = {'type':'robinson'}
    #         )
    #     )

    #     choromap = go.Figure(data = [data],layout = layout)

    #     plot(choromap)

    def deployment_report():
        webbrowser.open('http://127.0.0.1:8050/')




    HEIGHT = 550
    WIDTH = 1150

    root = ThemedTk(theme="plastik")#plactik comes from the module ttkthemes
    root.title('BeeHive')

    canvas = tk.Canvas(root, width = WIDTH, height = HEIGHT)
    canvas.pack()
    logo_fr = tk.Frame(root)
    logo_fr.place(relx=0.02, rely=0, relwidth=0.13, relheight=0.15)

    logo_image = tk.PhotoImage(file = 'C:\\Users\\Dmacm\\Desktop\\Asset Management\\app_files\\images\\BeeHive.png')
    logo_label=tk.Label(logo_fr, image = logo_image, anchor='w')
    logo_label.place(relwidth=1, relheight=1)

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    # filemenu.add_command(label="Connect", command=get_connected)
    # filemenu.add_command(label="Disonnect", command=database_disconnect)
    filemenu.add_command(label="Settings")
    filemenu.add_separator()
    filemenu.add_command(label="Exit")
    menubar.add_cascade(label="File", menu=filemenu)

    toolmenu = tk.Menu(menubar, tearoff=0)
    toolmenu.add_command(label="Activity Log", command=activity_log)
    toolmenu.add_command(label="Extract Asset Info", command=run_extract_equip)
    toolmenu.add_command(label="Extract Switch Info", command=run_extract_network_connections)
    toolmenu.add_command(label="Det Report", command=deployment_report)
    toolmenu.add_separator()
    toolmenu.add_command(label="Bulk Print 731", command=bulk_gen_731)
    toolmenu.add_command(label="DET Packing Label#")
    menubar.add_cascade(label="Tools", menu=toolmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About...")
    menubar.add_cascade(label="Help", menu=helpmenu)

    upper_frame_right = ttk.Frame (root)
    upper_frame_right.place(relx=0, rely=0.15, relwidth=0.15, relheight=0.85)

    button_left = ttk.Button(upper_frame_right, text='Add Asset', command=add_asset)
    button_left.place(relx=0.1, rely=0.01, relheight=0.08, relwidth=0.8)

    button_middle = ttk.Button(upper_frame_right, text='Remove Asset', command=delete_asset)
    button_middle.place(relx=0.1, rely=0.11, relheight=0.08, relwidth=0.8)

    button_middle = ttk.Button(upper_frame_right, text='Update Asset', command=combine_funcs(disable_selection, update_asset))
    button_middle.place(relx=0.1, rely=0.25, relheight=0.08, relwidth=0.8)

    button_middle_two = ttk.Button(upper_frame_right, text='View Comments', command=comments_log)
    button_middle_two.place(relx=0.1, rely=0.35, relheight=0.08, relwidth=0.8)

    button_left_two = ttk.Button(upper_frame_right, text='731 Selected Asset', command=gen_731)
    button_left_two.place(relx=0.1, rely=0.45, relheight=0.08, relwidth=0.8)


    button_left_three = ttk.Button(upper_frame_right, text='Network Management#')
    button_left_three.place(relx=0.1, rely=0.59, relheight=0.08, relwidth=0.8)

    button_left_three = ttk.Button(upper_frame_right, text='Fault Management#')
    button_left_three.place(relx=0.1, rely=0.69, relheight=0.08, relwidth=0.8)



    label_top_right = tk.Label(root, anchor='e')
    label_top_right.place(relx=0.2, rely=0.90, relwidth=0.8, relheight=0.05)

    label_connection = tk.Label(root, text='Connected to PostgreSQL', font=('Segoe UI', 8), anchor='e')
    label_connection.place(relx=0.2, rely=0.95, relwidth=0.8, relheight=0.04)

    lower_frame = ttk.Frame (root)
    lower_frame.place(relx=0.18, rely=0.03, relwidth=0.25, relheight=0.87)

    entry_filter = ttk.Entry(lower_frame)
    entry_filter.place(relx=0, rely=0, relwidth=0.70, relheight=0.06)

    # button_get_database = ttk.Button(lower_frame, text='Query', command=lambda: get_database(entry_filter.get()))
    # button_get_database.place(rely=0, relx=0.71, relheight=0.062, relwidth=0.29)

    button_get_database = ttk.Button(lower_frame, text='Query', command= get_database)
    button_get_database.place(rely=0, relx=0.71, relheight=0.062, relwidth=0.29)


    list_box_bottom = tk.Listbox(lower_frame, font=('Segoe UI', 10))
    try:
        list_box_bottom.bind("<<ListboxSelect>>", lambda x: display_asset())
    except:
        print('error, back tab used, tuple out of range')	
    list_box_bottom.place(rely=0.07, relx=0, relheight=0.93, relwidth=1)

    scrollbar = ttk.Scrollbar(list_box_bottom, orient='vertical', command=list_box_bottom.yview)
    scrollbar.pack(side='right', fill='y')

    # root.bind("<Control-f>", comments_log)

    update_asset()
    details_comments()
    root.config(menu=menubar)
    root.mainloop()

get_connected()
