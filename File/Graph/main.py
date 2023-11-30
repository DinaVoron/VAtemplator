import re
import numpy             as np
import pandas            as pd
import bs4
import requests
import spacy
from   spacy             import displacy
from   spacy.attrs       import LOWER, POS, DEP, ENT_TYPE, IS_ALPHA
from   spacy.matcher     import Matcher
from   spacy.tokens      import Span, Doc
import numpy
from   pathlib           import Path
import networkx          as nx
from   pyvis.network     import Network
import matplotlib.pyplot as plt
from   tqdm              import tqdm
import textacy
import os

# from   Module.OpenFile   import open_pdf, close, File

"""
python -m spacy download *****
https://spacy.io/usage/models

Российский конвейер, оптимизированный для ЦП. Компоненты: tok2vec, морфологизатор, парсер, отправитель, ner, Attribute_ruler, лемматизатор.
ru_core_news_sm		Эффективность / 14 Мб
					Словарь, синтаксис, сущности
ru_core_news_md		 / 39 Мб
					Словарь, синтаксис, сущности, векторы
ru_core_news_lg		Точность / 489 Мб
					Словарь, синтаксис, сущности, векторы
"""

"""
- ADJ:		adjective, e.g. big, old, green, incomprehensible, first
- ADP:		adposition (preposition/postposition) e.g. in, to, during
- ADV:		adverb, e.g. very, tomorrow, down, where, there
- AUX:		auxiliary, e.g. is, has (done), will (do), should (do)
- CONJ:		conjunction, e.g. and, or, but
- CCONJ:	coordinating conjunction, e.g. and, or, but
- DET:		determiner, e.g. a, an, the
- INTJ:		interjection, e.g. psst, ouch, bravo, hello
- NOUN:		noun, e.g. girl, cat, tree, air, beauty
- NUM:		numeral, e.g. 1, 2017, one, seventy-seven, IV, MMXIV
- PART:		particle, e.g. ‘s, not
- PRON:		pronoun, e.g I, you, he, she, myself, themselves, somebody
- PROPN:	proper noun, e.g. Mary, John, London, NATO, HBO
- PUNCT:	punctuation, e.g. ., (, ), ?
- SCONJ:	subordinating conjunction, e.g. if, while, that
- SYM:		symbol, e.g. $, %, §, ©, +, −, ×, ÷, =, :), emojis
- VERB:		verb, e.g. run, runs, running, eat, ate, eating
- X:		other, e.g. sfpksdpsxmsa
- SPACE:	space, e.g.

- ACL: 			clausal modifier of noun
- ACOMP: 		adjectival complement
- ADVCL: 		adverbial clause modifier
- ADVMOD: 		adverbial modifier
- AGENT: 		agent
- AMOD: 		adjectival modifier
- APPOS: 		appositional modifier
- ATTR: 		attribute
- AUX: 			auxiliary
- AUXPASS: 		auxiliary (passive)
- CASE: 		case marker
- CC: 			coordinating conjunction
- CCOMP: 		clausal complement
- COMPOUND: 	compound modifier
- CONJ: 		conjunct
- CSUBJ: 		clausal subject
- CSUBJPASS: 	clausal subject (passive)
- DATIVE: 		dative
- DEP: 			unclassified dependent
- DET: 			determiner
- DOBJ: 		direct object
- EXPL: 		expletive
- INTJ: 		interjection
- MARK: 		marker
- META: 		meta modifier
- NEG: 			negation modifier
- NOUNMOD: 		modifier of nominal
- NPMOD:		noun phrase as adverbial modifier
- NSUBJ:		nominal subject
- NSUBJPASS:	nominal subject (passive)
- NUMMOD:		number modifier
- OPRD:			object predicate
- PARATAXIS:	parataxis
- PCOMP:		complement of preposition
- POBJ:			object of preposition
- POSS:			possession modifier
- PRECONJ:		pre-correlative conjunction
- PREDET:		pre-determiner
- PREP:			prepositional modifier
- PRT:			particle
- PUNCT:		punctuation
- QUANTMOD:		modifier of quantifier
- RELCL:		relative clause modifier
- ROOT:			root
- XCOMP:		open clausal complement
"""

# file = open_pdf("Document/2.pdf")
# text = file.text(
# 	fl          = True,
# 	border      = [1, None],
# 	replacement = [
# 		# 
# 		(r"###.+?###",       "" ),
# 		# 
# 		(r" .+? ", "" ),
# 		(r" ",          "" ),
# 		(r"­",          "" ),
# 		(r"\s+",             " ")
# 	])
# close(file)

text = 'Какой балл был в 2023 году по Програмной инженерии?'
# text = """Правила приема в ДВФУ на обучение по программам бакалавриата в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
# Правила приема в ДВФУ на обучение по программам специалитета в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
# Правила приема в ДВФУ на обучение по программам магистратуры в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
# Правила приема в ДВФУ на обучение по программам подготовки научных кадров в аспирантуре в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
# Правила приема в ДВФУ на обучение по программам подготовки научно-педагогических кадров в аспирантуре в 2023 году определяют особенности приема в федеральное государственное автономное образовательное учреждение высшего образования Дальневосточный федеральный университет / ДВФУ / Университет.
# Правила приема в ДВФУ в 2023 году определяют особенности приема на первый курс в 2023/2024 учебном году на места в рамках контрольных цифр приема на обучение за счет бюджетных ассигнований федерального бюджета и по договорам об образовании, заключаемым при приеме на обучение за счет средств физических или юридических лиц.
# Правила приема в ДВФУ в 2023 году определяют особенности приема на первый курс в 2023/2024 учебном году на обучение за счет бюджетных ассигнований федерального бюджета и по договорам об образовании для следующих категорий граждан: обучавшихся в организациях осуществляющих образовательную деятельность, завершивших освоение образовательных программ среднего общего образования и успешно прошедших государственную итоговую аттестацию, проходивших обучение за рубежом и вынужденных прервать его в связи с недружественными действиями иностранных государств.
# Обучавшихся в организациях осуществляющих образовательную деятельность, расположенных на территориях Донецкой Народной Республики, Луганской Народной Республики, Запорожской области, Херсонской области.
# Завершивших освоение образовательных программ среднего общего образования и успешно прошедших государственную итоговую аттестацию на территориях Донецкой Народной Республики, Луганской Народной Республики, Запорожской области, Херсонской области.
# Проходивших обучение за рубежом и вынужденных прервать его в связи с недружественными действиями иностранных государств, на основании частей 7 и 8 статьи 5 Федерального закона от 17 февраля 2023 г. № 19-ФЗ «Об особенностях правового регулирования отношений в сферах образования и науки», а также постановления Правительства Российской Федерации от 3 апреля 2023 г. № 528 «Об утверждении особенностей приема на обучение по образовательным программам высшего образования в 2023 году»."""
text = re.sub(r"\s+", " ", text, flags=re.DOTALL)

# print("\nИСХОДНЫЙ ТЕКСТ:\n", text, "\n\n\n")



class Token:
	def __init__(self, token):
		self.p_index = [token.i]
		self.p_text  = [token.text]
		self.p_lemma = [token.lemma_]
		self.p_pos   = [token.pos_]
		if token.dep_ == "ROOT":
			self.p_con_index = None
			self.p_con_dep   = None
			self.p_con_text  = None
			self.p_con_lemma = None
		else:
			self.p_con_index   = token.head.i
			self.p_con_dep   = token.dep_
			self.p_con_text  = token.head.text
			self.p_con_lemma = token.head.lemma_

	def __repr__(self):
		return f"{self.index}: {self.p_text}"

	def sort(self):
		pass

	@property
	def list_index(self):
		return self.p_index

	@property
	def list_text(self):
		return self.p_text
	@property
	def text(self):
		return " ".join(self.p_text)

	@property
	def list_lemma(self):
		return self.p_lemma
	@property
	def lemma(self):
		return " ".join(self.p_lemma)

	@property
	def list_pos(self):
		return self.p_pos

	@property
	def con_index(self):
		return self.p_con_index

	@property
	def con_dep(self):
		return self.p_con_dep

	@property
	def con_text(self):
		return self.p_con_text

	@property
	def con_lemma(self):
		return self.p_con_lemma

class Node:
	def __init__(self, data, step_index):
		self.p_id    = data["ID"] + step_index
		self.p_text  = data["Text"]
		self.p_lemma = data["Lemma"]
		self.p_pos   = data["Pos"]

	@property
	def index(self):
		return self.p_id

	@property
	def text(self):
		return self.p_text

	@property
	def lemma(self):
		return self.p_lemma

	@property
	def pos(self):
		return self.p_pos

class Graph:
	def __init__(self):
		self.p_graph    = nx.DiGraph()

		self.static_index = 0
		self.static_layer = 1

	def add_DataFrame(self, df):
		step = 0
		for i, row in df.iterrows():
			self.p_graph.add_node(
				row["ID"] + self.static_index,
				data  = Node(row, self.static_index),
				layer = self.static_layer
				)
			step += 1
		for i, row in df.iterrows():
			if row["Con Dep"]:
				self.p_graph.add_edge(
					row["ID"]     + self.static_index,
					row["Con ID"] + self.static_index,
					data  = row["Con Dep"],
					layer = self.static_layer
					)
		self.static_index += step
		self.static_layer += 1

	def visible(self, pattern, shape = ["triangle", "dot", "dot", "box"], color = ["#ffdd00", "#0055cc", "#00aacc", "#7a6a59"], size = [20, 12, 12, 10]):
		# Отображение графа
		net = Network(height = "760px", width = "100%",
			bgcolor = "#222222", font_color = "white",
			notebook = False,   directed = True,
			select_menu = True, filter_menu = True)
		net.set_options("""const options = {
		  "interaction": {
		    "navigationButtons": true
		  }
		}""")
		if pattern == "Text":
			for i, node in enumerate(self.p_graph.nodes):
				net.add_node(
					node,
					label = self.p_graph.nodes[i]['data'].text,
					title = f"> #{self.p_graph.nodes[i]['data'].index}"\
							f"\n> {self.p_graph.nodes[i]['data'].text}"\
							f"\n> {self.p_graph.nodes[i]['data'].lemma}",
					layer = f"layer: #{self.p_graph.nodes[i]['layer']}",
					shape = shape[1],
					color = color[1],
					size  = size [1]
					)
		elif pattern == "Lemma":
			for i, node in enumerate(self.p_graph.nodes):
				net.add_node(
					node,
					label = self.p_graph.nodes[i]['data'].lemma,
					title = f"> #{self.p_graph.nodes[i]['data'].index}"\
							f"\n> {self.p_graph.nodes[i]['data'].text}"\
							f"\n> {self.p_graph.nodes[i]['data'].lemma}",
					layer = f"layer: #{self.p_graph.nodes[i]['layer']}",
					shape = shape[1],
					color = color[1],
					size  = size [1]
					)
		for i, edge in enumerate(self.p_graph.edges):
			net.add_edge(
				edge[0],
				edge[1],
				label = self.p_graph.edges[edge[0], edge[1]]['data'],
				layer = f"layer #{self.p_graph.edges[edge[0], edge[1]]['layer']}"
				)
		net.show('graph.html', notebook=False)

def list_token_to_pandas(list_token):
	df = pd.DataFrame(
		columns = [
			"ID", "Con ID"
			"Index", "Text", "Lemma", "Pos",
			"Con Index", "Con Dep"
			]
		)
	# ЗАПОЛНЕНИЕ СТРОК ДАННЫМИ
	for token in list_token:
		token.sort()
		row = {
			"ID":			None,
			"Con ID":		None,
			"Index":		token.list_index,
			# "List Text":	token.list_text,
			"Text":			token.text,
			# "List Lemma":	token.list_lemma,
			"Lemma":		token.lemma,
			"Pos":			token.list_pos,
			"Con Index":	token.con_index,
			"Con Dep":		token.p_con_dep
			# "Con Text":	token.p_con_text,
			# "Con Lemma": 	token.p_con_lemma
		}
		df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
	# ОБРАБОТКА ДАННЫХ
	# Обработка строки, этап 1
	for i, row_iter in df.iterrows():
		df["ID"][i:i+1] = i
		if row_iter["Con Dep"]:
			for j, row in df.iterrows():
				if i != j:
					# print(row_iter["Con Index"], row["Index"])
					if row_iter["Con Index"] in row["Index"]:
						df["Con ID"][i:i+1] = j
						break
		else:
			pass
	# Обработка строки, этап 2
	df = df.drop(["Index", "Con Index"], axis=1)
	return df

def create_list_token(sent):
	# list_token = [token for token in sent]

	# i = 0
	# while i < len(list_token):
	# 	pass
	# 	# Определение стоп-слов
	# 	# if list_token[i].is_stop:
	# 	# 	del list_token[i]
	# 	# else:
	# 	# 	i += 1
	return [Token(token) for token in sent]




nlp      = spacy.load("ru_core_news_lg")
graph    = Graph()
document = nlp(text)

for n, sent in enumerate(document.sents):
	print(f"Длина: {len(sent)}\n", f" Текст: {sent}")

	print("  ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––\n  Именованные сущности:")
	for entity in sent.ents:
		print(f"  {entity.text:<120}{entity.label_:<30}") 

	print("  ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––\n  Токены:")
	for token in sent:
		print(" ", f"{token.text:<20}{token.lemma_:<20}{token.is_stop:<5}{token.pos_:<20}{token.dep_:<20}{token.head.text:<20}{token.i:<5}{token.head.i:<5}")

	list_token = create_list_token(sent)

	df = list_token_to_pandas(list_token)
	graph.add_DataFrame(df)

# Text  - Вывод тест
# Lemma - Вывод лексем (начальная форма)
graph.visible("Text")



"""
html = displacy.render(document, style="dep", jupyter=False)
output_path = Path("./plot-1.svg")
output_path.open("w", encoding="utf-8").write(html)

html = displacy.render(document, style='ent', jupyter=False)
output_path = Path("./plot-2.svg")
output_path.open("w", encoding="utf-8").write(html)
"""