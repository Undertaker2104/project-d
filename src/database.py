import sqlite3

class Database:
	def rows_that_arent_in_table(self, db_table, code_col, table):
		not_in_db = []
		cur = self.con.cursor()
		for row in table:
			code = row[code_col]
			# can't parameterize tables so have to do it the dirty way
			cur.execute(f"""
				SELECT EXISTS(SELECT * FROM {db_table} WHERE code = ?)
			""", (code,))
			res = cur.fetchone()
			if res[0] == 0:
				not_in_db.append(row)
		return not_in_db

	def rows_add(self, db_table, key_col, desc_col, memo_col, table):
		cur = self.con.cursor()
		cur.executemany(f"""
			INSERT OR IGNORE INTO {db_table}(code, description, memo)
			VALUES (?, ?, ?)
		""", ((r[key_col], r[desc_col], r[memo_col]) for r in table if r[key_col] is not None))
		cur.close()

	def update_token_frequencies(self, datasets, text_col, table):
		d = dict()
		for row in table:
			tokens = datasets.tokenize(row[text_col])
			for token in tokens:
				if token not in datasets.trivial_tokens():
					d[token] = d.get(token, 0) + 1

		cur = self.con.cursor()
		cur.executemany("""
			INSERT OR IGNORE INTO token_frequency(
				token,
				frequency
			) VALUES (:token, :frequency)
			ON CONFLICT	DO UPDATE SET
				frequency = frequency + :frequency
			WHERE token = :token
		""", [{"token": t, "frequency": f} for t, f in d.items()])
		cur.close()

	def update_keywords(self, datasets, key_col, desc_col, table):
		for row in table:
			tokens = datasets.tokenize(row[desc_col])
			cur = self.con.cursor()
			freqs = []
			for tok in tokens:
				r = cur.execute("""
					SELECT frequency FROM token_frequency WHERE token = ?
				""", (tok,)).fetchone()
				if r is not None:
					freqs.append({"token": tok, "frequency": r[0]})
			freqs.sort(key=lambda x: x["token"])
			freqs.sort(key=lambda x: x["frequency"], reverse=True)
			for f in freqs:
				cur.execute("""
					INSERT OR IGNORE INTO keyword(token, code)
					VALUES (?, ?)
				""", (f["token"], row[key_col]))
			cur.close()

	def update_parts(self, datasets, key_col, desc_col, table):
		# figure out what the parts are
		parts = set()
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT token FROM token_frequency
			WHERE frequency > 3
		""")
		for token in res.fetchall():
			token = token[0]
			if token not in datasets.lexicon() and not token.isnumeric() and token not in datasets.ignored_tokens():
				parts.add(token)
				
		# add rows that contain a token that is a "part" to the db
		rows = []
		for row in table:
			tokens = datasets.tokenize(row[desc_col])
			for part in parts:
				if part in tokens:
					rows.append((part, row[key_col]))
		cur.executemany("""
			INSERT OR IGNORE INTO part(name, code) VALUES(?, ?)
		""", rows)
		cur.close()

	def get_part_groups(self):
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT name, GROUP_CONCAT(code, "\n\t")
			FROM part GROUP BY name
		""")
		groups = res.fetchall()
		cur.close()
		return groups

	def get_part_groups_where(self, part):
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT name, GROUP_CONCAT(code, "\n\t")
			FROM part WHERE name = ? GROUP BY name
		""", (part,))
		groups = res.fetchall()
		cur.close()
		return groups

	def get_parts(self):
		res = self.con.execute("""
			SELECT DISTINCT name FROM part
		""")
		for r in res.fetchall():
			yield r[0]

	def get_keywords(self):
		res = self.con.execute("""
			SELECT DISTINCT token FROM keyword
		""")
		for r in res.fetchall():
			yield r[0]

	def get_keyword_groups(self):
		cur = self.con.cursor()
		# Group items by their two most frequent keywords
		# I got this query from Gemini, I don't really know how it works
		res = cur.execute("""
			WITH top_two_pairs AS (
				SELECT code, keyword.token AS keyword_token, frequency,
					ROW_NUMBER() OVER (PARTITION BY code ORDER BY frequency DESC)
					AS rank
				FROM keyword
				INNER JOIN token_frequency
				ON keyword.token = token_frequency.token
			),
			high_freq_pairs AS (
				SELECT code, GROUP_CONCAT(keyword_token, ", ") AS tokens
				FROM top_two_pairs
				WHERE rank <= 2
				GROUP BY code
			)
			SELECT tokens, GROUP_CONCAT(code, "\n\t")
			FROM high_freq_pairs
			GROUP BY tokens;
		""")
		groups = res.fetchall()
		cur.close()
		return groups

	def get_keyword_groups_where(self, *keywords):
		groups = self.get_keyword_groups()
		needle = ", ".join(keywords)
		return [g for g in groups if needle in g[0]]

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
