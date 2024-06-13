import logging
import sqlite3
import lib

logger = logging.getLogger(__name__)

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
		logger.debug(f"{len(not_in_db)} rows not found in table {db_table}")
		return not_in_db

	def rows_add(self, db_table, key_col, desc_col, memo_col, table):
		cur = self.con.cursor()
		cur.executemany(f"""
			INSERT OR IGNORE INTO {db_table}(code, description, memo)
			VALUES (?, ?, ?)
		""", [(r[key_col], r[desc_col], r[memo_col]) for r in table])
		cur.close()

	def update_token_frequencies(self, freqs):
		logger.debug(f"Inserting/updating {len(freqs)} token_frequency rows")
		cur = self.con.cursor()
		# print(freqs)
		cur.executemany("""
			INSERT OR IGNORE INTO token_frequency(
				token,
				frequency
			) VALUES (:token, :frequency)
			ON CONFLICT	DO UPDATE SET
				frequency = frequency + :frequency
			WHERE token = :token
		""", freqs)
		cur.close()

	def update_keywords(self, key_col, desc_col, table):
		for row in table:
			tokens = lib.tokenize(row[desc_col])
			cur = self.con.cursor()
			freqs = []
			for tok in tokens:
				r = cur.execute("""
					SELECT frequency FROM token_frequency WHERE token = ?
				""", (tok,)).fetchone()
				if r is not None:
					freqs.append({"token": tok, "frequency": r[0]})
			freqs.sort(key=lambda x: x["frequency"], reverse=True)
			for f in freqs[:2]:
				cur.execute("""
					INSERT OR IGNORE INTO keyword(token, code)
					VALUES (?, ?)
				""", (f["token"], row[key_col]))
			cur.close()
				
		
	def close(self):
		self.con.commit()
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
			CREATE TABLE IF NOT EXISTS token(
				token TEXT PRIMARY KEY
			);
			CREATE TABLE IF NOT EXISTS token_frequency(
				token     TEXT    PRIMARY KEY,
				frequency INTEGER DEFAULT 0
			);
			CREATE TABLE IF NOT EXISTS keyword(
				token TEXT,
				code  TEXT,
				FOREIGN KEY(token) REFERENCES token(token),
				FOREIGN KEY(code) REFERENCES item(code),
				PRIMARY KEY(token, code)
			);
			CREATE TABLE IF NOT EXISTS part(
				name TEXT,
				code TEXT,
				FOREIGN KEY(code) REFERENCES item(code),
				FOREIGN KEY(name) REFERENCES token(token),
				PRIMARY KEY(name, code)
			);
			COMMIT;
		""")
	
		cur.close()
