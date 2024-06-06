import sqlite3

class Database:
	def rows_that_arent_in_table(self, db_table, col, rows):
		not_in_db = []
		cur = self.con.cursor()
		for row in rows:
			code = row[col]
			# can't parameterize tables so have to do it the dirty way
			cur.execute(f"""
				SELECT EXISTS(SELECT * FROM {db_table} WHERE code = ?)
			""", (code,))
			res = cur.fetchone()
			if res[0] == 0:
				not_in_db.append(row)
		return not_in_db

	def close(self):
		self.con.close()

	def open_else_create(self, path):
		self.con = sqlite3.connect(path)
		cur = self.con.cursor()
	
		cur.executescript("""
			BEGIN;
			CREATE TABLE IF NOT EXISTS item(
				code TEXT PRIMARY KEY
			);
			CREATE TABLE IF NOT EXISTS actionscope(
				code        TEXT PRIMARY KEY,
				description TEXT,
				memo        TEXT,
				FOREIGN KEY(code) REFERENCES item(code)
			);
			CREATE TABLE IF NOT EXISTS job_order(
				code        TEXT PRIMARY KEY,
				description TEXT,
				memo        TEXT,
				FOREIGN KEY(code) REFERENCES item(code)
			);
			CREATE TABLE IF NOT EXISTS word_frequency(
				word      TEXT    PRIMARY KEY,
				frequency INTEGER DEFAULT 0
			);
			CREATE TABLE IF NOT EXISTS keyword(
				word TEXT,
				code TEXT,
				FOREIGN KEY(word) REFERENCES word_frequency(word),
				FOREIGN KEY(code) REFERENCES item(code),
				PRIMARY KEY(word, code)
			);
			CREATE TABLE IF NOT EXISTS part(
				name TEXT,
				code TEXT,
				FOREIGN KEY(code) REFERENCES item(code),
				PRIMARY KEY(name, code)
			);
			COMMIT;
		""")
	
		cur.close()
