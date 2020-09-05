from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivymd.uix.snackbar import Snackbar
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressloader import MDProgressLoader
from kivymd.toast import toast
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.event import EventDispatcher
import pyrebase
import time
from json import dumps
from urllib.request import urlopen
from kivy.network.urlrequest import UrlRequest
import os

config = {
  "apiKey": "AIzaSyD417InV5qBDmV6Z-UALNvCREiWh6I6tKA",
  "authDomain": "memories-e4f33.firebaseapp.com",
  "databaseURL": "https://memories-e4f33.firebaseio.com",
  "storageBucket": "memories-e4f33.appspot.com",
  "serviceAccountId": "kukrisaccount369@memories-e4f33.iam.gserviceaccount.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
storage = firebase.storage()
user=None
EmailID = None
users = []
keys = []
debug = True
Refresher = "False"
idToken = None
localId = None
FileNumber = 0
auth = firebase.auth()

class LoginScreen(Screen, EventDispatcher):
	checkerLS = StringProperty("")
	Refresh = StringProperty("")
	def sign_in(self):
		global user, EmailID, debug
		self.checkerLS = "NoError"
		email = self.ids.email.text
		password = self.ids.password.text
		EmailID = email[:-10]
		try:
			user = auth.sign_in_with_email_and_password(email, password)
		except:
			self.checkerLS = "Error"
			Snackbar(text="Invalid Email or Password").show()
		refresh_token = user['refreshToken']
		self.refresh_token_file = MDApp.get_running_app().user_data_dir + "\\refresh_token.txt"
		self.user_meta_data_file = MDApp.get_running_app().user_data_dir + "\\user_meta_data.txt"
		if debug:
			print("Saving the refresh token to file: ", self.refresh_token_file)
		with open(self.refresh_token_file, "w") as f:
			f.write(refresh_token)
		with open(self.user_meta_data_file, "w") as f:
			f.write(EmailID)

	def check_refresh(self):
		self.Refresh = 'False'
		if Refresher=='True':
			self.Refresh = 'True'
		else:
			Snackbar(text='No Previous Login Details Found!',
		padding="20dp").show()

class CreateAccountScreen(Screen):
	checkerCAS = StringProperty("")
	def create_account(self):
		self.checkerCAS = "NoError"
		email = self.ids.email.text
		password = self.ids.password.text
		if password == self.ids.cnfrm_password.text :
			auth = firebase.auth()
			try:
				auth.create_user_with_email_and_password(email, password)
				Snackbar(text='New Account Created Succesfully. You May Sign In Now.').show()
			except:
				self.checkerCAS = "Error"
				Snackbar(text='Invalid Email or Error While Conecting To The Internet').show()
			print(self.checkerCAS)
		else:
			self.checkerCAS = "Error"
			Snackbar(text='Passwords Do Not Match Please Check Again').show()

class CreateProfileScreen(Screen):
	checkerCPS = StringProperty("")
	def openfile(self):
		path = '/'  # path to the directory that will be opened in the file manager
		self.file_manager = MDFileManager(
			exit_manager=self.exit_manager_function,  # function called when the user reaches directory tree root
			select_path=self.select_path_function,  # function called when selecting a file/directory
		)
		self.file_manager.show(path)

	def exit_manager_function(self,obj):
		self.file_manager.close()
	
	def select_path_function(self,path):

		storage.child(f"ProfilePhotos/{EmailID}/current").put(f"{path}", user['idToken'])
		self.exit_manager_function()
		label = MDLabel(text='Profile Photo Updated Successfully.',pos_hint={'center_y':0.1},halign='center',font_style='H6',theme_text_color='Custom',text_color=(0,1,0,1))
		self.add_widget(label)

	def menu(self):
		
		menu_items = [{"icon": "face-agent", "text": "Male"}, {"icon": "face-woman", "text": "Female"}]
		
		self.menu_open = MDDropdownMenu(
			caller=self.ids.drop_item,
			items=menu_items,
			position="auto",
			callback=self.set_item,
			width_mult=4,
		)
		self.menu_open.open()

	def set_item(self, instance):
		self.ids.drop_item.set_item(instance.text)
		self.menu_open.dismiss()
	
	def agree_and_continue(self):
		if self.ids.year_of_birth.text>"2010" or self.ids.year_of_birth.text<"1940":
			Snackbar(text='Looks Like You Are Not Eligible To Use This App Because Of Your Given DOB').show()
		if len(self.ids.mobile_number.text) != 10:
			Snackbar(text='Invalid Mobile Number. Please Check Again').show()
		try:
			self.checkerCPS = 'NoError'
			data = {'first_name':f'{self.ids.first_name.text}',
					'complete_name':f'{self.ids.first_name.text} {self.ids.middle_name.text} {self.ids.last_name.text}',
					'address': f'{self.ids.address.text}',
					'year_of_birth': f'{self.ids.year_of_birth.text}',
					'mobile_number': f'{self.ids.mobile_number.text}'
			}  
			db.child("Users").child(f"{EmailID}").set(data)
		except:
			self.checkerCPS = 'Error'
			Snackbar(text='We Are Having Trouble Connecting To The Internet..Please Try Again Later').show()

class AddFriendsScreen(Screen):
	n1,n2,n3,n4,n5,n6,n7 = [int(0) for i in range(7)]
	users_all = ListProperty(users)
	keys_all = ListProperty(keys)
	FNumber = 0
	def sendreq(self, key):
		lst = [str(x) for x in range(12)]
		for a in lst:
			if str(a) in key:
				i = int(a)
		icon = IconLeftWidget(icon='check-circle', )
		if key=='list1' and self.n1==0:
			data = {'sent_requests': f'{self.keys_all[i-1]}'}
			db.child("Users").child(f"{EmailID}").child('Friends').child(f'f{self.FNumber}').set(data)
			self.FNumber += 1
			self.ids.list1.add_widget(icon)
			Snackbar(text='Request Sent', padding='80dp').show()
			self.n1+=1
		else:
			Snackbar(text='Request Already Sent!',padding='80dp').show()
		if key=='list2' and self.n2==0:
			self.ids.list2.add_widget(icon)
			data = {'sent_requests': f'{self.keys_all[i-1]}'}
			db.child("Users").child(f"{EmailID}").child('Friends').child(f'f{self.FNumber}').set(data)
			self.FNumber += 1
			Snackbar(text='Request Sent', padding='80dp').show()
			self.n2+=1
		else:
			Snackbar(text='Request Already Sent!',padding='80dp')
		if key=='list3' and self.n3==0:
			data = {'sent_requests': f'{self.keys_all[i-1]}'}
			db.child("Users").child(f"{EmailID}").child('Friends').child(f'f{self.FNumber}').set(data)
			self.FNumber += 1
			self.ids.list3.add_widget(icon)
			Snackbar(text='Request Sent', padding='80dp').show()
			self.n3+=1
		else:
			Snackbar(text='Request Already Sent!',padding='80dp')

class HomeScreen(Screen):
	users_all = ListProperty(users)
	keys_all = ListProperty(keys)
	userid = StringProperty(EmailID)
	print(userid)
	def upload(self):
		path = '/'  # path to the directory that will be opened in the file manager
		self.file_manager = MDFileManager(
			exit_manager=self.exit_manager_function,  # function called when the user reaches directory tree root
			select_path=self.select_path_function  # function called when selecting a file/directory
		)
		self.file_manager.show(path)
		toast('Uploading May Take A few Seconds. Please Keep Patience')

	def exit_manager_function(self,obj):
		self.file_manager.close()

	
	def select_path_function(self,path):
		global FileNumber
		print(f'https://firebasestorage.googleapis.com/v0/b/memories-e4f33.appspot.com/o/Uploads%2F{EmailID}%2Ff{FileNumber}?alt=media')
		while True:	
			try:
				urlopen(f'https://firebasestorage.googleapis.com/v0/b/memories-e4f33.appspot.com/o/Uploads%2F{EmailID}%2Ff{FileNumber}?alt=media')
				FileNumber += 1
			except:
				break
		storage.child(f"Uploads/{EmailID}/f{FileNumber}").put(f"{path}")
		FileNumber += 1
		toast(text='Photo Uploaded Successfully')

class MyApp(MDApp):
	def build(self):
		global users
		global keys
		all_users = db.child("Users").get()
		for user in all_users.each():
			name = db.child("Users").child(f'{user.key()}').child('complete_name').get()
			keys.append(user.key())
			users.append(name.val())
		self.theme_cls.primary_palette = "DeepPurple"
		master = Builder.load_file("main.kv")
		return master
		
	def on_start(self):

		self.refresh_token_file = MDApp.get_running_app().user_data_dir + "\\refresh_token.txt"
		self.user_meta_data_file = MDApp.get_running_app().user_data_dir + "\\user_meta_data.txt"
		if debug:
			print("Looking for a refresh token in:", self.refresh_token_file)
		if os.path.exists(self.refresh_token_file):
			self.load_saved_account()


	def load_saved_account(self):
		if debug:
			print("Attempting to log in a user automatically using a refresh token.")
		self.load_refresh_token()
		refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + "AIzaSyD417InV5qBDmV6Z-UALNvCREiWh6I6tKA"
		refresh_payload = dumps({"grant_type": "refresh_token", "refresh_token": self.refresh_token})
		UrlRequest(refresh_url, req_body=refresh_payload,
				   on_success=self.successful_account_load,
				   on_failure=self.failed_account_load,
				   on_error=self.failed_account_load)
	
	def load_refresh_token(self):
		global EmailID
		if debug:
			print("Loading refresh token & Meta Data from file: ", self.refresh_token_file)
		with open(self.refresh_token_file, "r") as f:
			self.refresh_token = f.read()
		with open(self.user_meta_data_file, "r") as f:
			EmailID = f.read()
			print(EmailID)
	
	def successful_account_load(self, urlrequest, loaded_data):
		global Refresher, idToken
		if debug:
			print("Successfully logged a user in automatically using the refresh token")
		idToken = loaded_data['id_token']
		localId = loaded_data['user_id']
		print(loaded_data)
		Refresher = 'True'
	
	def failed_account_load(self, *args):
		if debug:
			print("Failed to load an account.", args)

	def callback(self):
		pass

MyApp().run()