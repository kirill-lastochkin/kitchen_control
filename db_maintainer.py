import sqlite3

class DbMaintainer:
	def init(self, db_dir):
		self.name = db_dir + "recipes_db"
		sqlite3.connect(self.name)

		# create tables

	def update_db(self, update_filepath, user_id):
		pass