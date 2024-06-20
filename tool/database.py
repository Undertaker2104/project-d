from console import print_info
from summarize import Summarizer

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

	def update_memos(self, key_col, memo_col, table):
		cur = self.con.cursor()
		cur.executemany("""
			UPDATE OR IGNORE actionscope
			SET memo_summarized = ?
			WHERE code = ?
		""", ((r[memo_col], r[key_col]) for r in table))
		

	def rows_add_actionscope(self, key_col, desc_col, memo_col, table):
		cur = self.con.cursor()
		cur.executemany("""
			INSERT OR IGNORE INTO actionscope(code, description, memo)
			VALUES (?, ?, ?)
		""", ((r[key_col], r[desc_col], r[memo_col]) for r in table))
		cur.close()

	def rows_add_job_order(self, key_col, desc_col, memo_col, solution_col, table):
		cur = self.con.cursor()
		cur.executemany("""
			INSERT OR IGNORE INTO job_order(code, description, memo, realized_solution)
			VALUES (?, ?, ?, ?)
		""", ((r[key_col], r[desc_col], r[memo_col], r[solution_col])
		       for r in table if r[key_col] is not None))
		cur.close()

	def update_token_frequencies(self, datasets, text_col, table):
		d = dict()
		for row in table:
			tokens = datasets.tokenize(row[text_col])
			for token in tokens:
				if token not in datasets.trivial_tokens() and not token.isnumeric():
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

	def update_parts(self, datasets, key_col, desc_col, sol_col, table):
		# figure out what the parts are
		parts = set()
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT token FROM token_frequency
			WHERE frequency > 3
		""")
		for token in res.fetchall():
			token = token[0]
			if token in datasets.parts_that_are_in_lexicon():
				parts.add(datasets.lem_dict().get(token, token))
			elif token not in datasets.lexicon() and not token.isnumeric() and token not in datasets.ignored_tokens():
				parts.add(datasets.lem_dict().get(token, token))
				
		# add rows that contain a token that is a "part" to the db
		rows = []
		for row in table:
			tokens = datasets.tokenize(row[desc_col])
			if sol_col != None:
				if sol_text := row[sol_col]:
					tokens.extend(datasets.tokenize(sol_text))
			for part in parts:
				if part in tokens:
					rows.append((part, row[key_col]))
		cur.executemany("""
			INSERT OR IGNORE INTO part(name, code) VALUES(?, ?)
		""", rows)
		cur.close()

	def update_summarizations_actionscopes(self, key_col, memo_col, table):
		summarizer = Summarizer()

		memo_summs = [None] * len(table)
		for row in range(len(table)):
			memo = table[row][memo_col]
			if memo and len(memo) > 50:
				print_info(f"summarizing memo {table[row][key_col]}...")
				memo_summs[row] = summarizer.summarize(memo)

		cur = self.con.cursor()
		cur.executemany("""
			UPDATE actionscope
			   SET memo_summarized = ?
			 WHERE code = ?
			VALUES (?, ?)
		""", zip((r[key_col] for r in table), memo_summs))
		cur.close()


	def update_summarizations_job_orders(self, key_col, memo_col, sol_col, table):
		summarizer = Summarizer()

		memo_summs = [None] * len(table)
		for row in range(len(table)):
			memo = table[row][memo_col]
			if memo and len(memo) > 50:
				print_info(f"summarizing memo {table[row][key_col]}...")
				memo_summs[row] = summarizer.summarize(memo)

		sol_summs = [None] * len(table)
		for row in range(len(table)):
			solution = table[row][sol_col]
			if solution and len(solution) > 50:
				print_info(f"summarizing solution {table[row][key_col]}...")
				sol_summs[row] = summarizer.summarize(solution)

		cur = self.con.cursor()
		cur.executemany("""
			UPDATE job_order
			   SET memo_summarized = ?
			 WHERE code = ?
			VALUES (?, ?)
		""", zip((r[key_col] for r in table), memo_summs))

		cur.executemany("""
			UPDATE job_order
			   SET realized_solution_summarized = ?
			 WHERE code = ?
			VALUES (?, ?)
		""", zip((r[key_col] for r in table), solution_summarization))
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

	def get_descriptions(self, code):
		descs = []
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT description FROM actionscope WHERE code = ?
		""", (code,))
		if desc := res.fetchone():
			descs.extend(desc)
		res = cur.execute("""
			SELECT description FROM job_order WHERE code = ?
		""", (code,))
		if desc := res.fetchone():
			descs.extend(desc)
		cur.close()
		return descs

	def get_memos(self, code):
		memos = []
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT memo FROM actionscope WHERE code = ?
		""", (code,))
		if memo := res.fetchone():
			memos.extend(memo)
		res = cur.execute("""
			SELECT memo FROM job_order WHERE code = ?
		""", (code,))
		if memo := res.fetchone():
			memos.extend(memo)
		cur.close()
		return memos

	def get_solution(self, code):
		cur = self.con.cursor()
		res = cur.execute("""
			SELECT realized_solution FROM job_order WHERE code = ?
		""", (code,)).fetchone()
		if res:
			return res[0]
		else:
			return None

	def get_context(self, code):
		context = []
		for mem in self.get_memos(code):
			if mem is not None:
				context.append(mem)
		if solution := self.get_solution(code):
			context.append(solution)
		return '\n'.join(context)

	def close(self):
		self.con.commit()
		self.con.close()

	def open_else_create(self, path):
		self.con = sqlite3.connect(path)
		cur = self.con.cursor()
	
		cur.executescript("""
			BEGIN;
			CREATE TABLE IF NOT EXISTS actionscope(
				code            TEXT PRIMARY KEY,
				description     TEXT,
				memo            TEXT,
				memo_summarized TEXT
			);
			CREATE TABLE IF NOT EXISTS job_order(
				code                         TEXT PRIMARY KEY,
				description                  TEXT,
				memo                         TEXT,
				memo_summarized              TEXT,
				realized_solution            TEXT,
				realized_solution_summarized TEXT
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
				PRIMARY KEY(name, code)
			);
			COMMIT;
		""")
	
		cur.close()
