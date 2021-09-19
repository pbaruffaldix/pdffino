#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
"""
# pdffino.py

short pdf library, basato sulle specifiche 1.7 del pdf

## Versioni

### Ver. 0.1 2020-10

- gestisce solo una pagina
- gestisce solo 2 elementi, fissi

### Ver. 0.2 2020-10-31

- multilinea
- stili
- markdown base

### Ver. 0.3 2020-11-04

- Dizionario info

## Ver. 0.4 2020-11-08

## Metodi

### Stile libero

Per scrivere dei testi, senza preoccuparsi di aspetti relativi alla
formattazione può bastare la funzione "paragraph", interna all'oggetto pdf

### Stile Markdown semplificato

Non include tutte le funzionalità del formato markdown ma gestisce i titoli, che sono gli elementi più importanti

## to do

### funzionalità indispensabili

1. linee e elementi grafici
2. "outline", albero dei bookmarks
3. Unicode
4. annotazioni
5. colori

### wish list

1. markdown avanzato con:
	1. grassetto e italico
	2. liste semplici
	3. liste numerate



"""
import datetime, time

S_GREY = "0 Tr\n 0.5 g"
S_STROKE = "1 Tr\n1 w"
S_SUPERSCRIPTED = "5 Ts"
S_SUBSCRIPTED = "-5 Ts"
S_NORMAL = "0 Tr\n 0 g"
DELIMITATORI = "()<>[]{}/%"

A4HEIGHT = 792

def main_cli():
	"""
	CLI interface
	"""
	test()


def pdf_dz(tipo, sequenza):
	"""
	converte in un dizionario pdf
	:return: str
	"""
	txt = "<< /Type /%s\n" % tipo
	pari = False
	for uno in sequenza:
		if isinstance(uno, int):  # riferimento ad oggetto
			txt += '%s 0 R' % uno
		elif isinstance(uno, list):  # lista
			txt += '['
			for due in uno:
				if isinstance(due, int):  # lista di riferimenti
					txt += '%s 0 R ' % due
			txt = txt[:-1] + ']'
		elif uno.isdigit():
			txt += "%s" % uno  # numero da non trasformare
		else:
			if uno[0] in DELIMITATORI:
				txt += "%s" % uno
			else:
				txt += "/%s" % uno
		txt += [" ", "\n"][pari]
		pari = not pari
	txt += ">>"
	return txt


def pdf_str(txt1):
	"""
	Converte in una stringa
	:return: str
	"""
	for c1 in DELIMITATORI:
		txt1 = txt1.replace(c1, '\\' + c1)
	return '(%s)' % txt1
	return txt


class PDF():
	def __init__(self, ver='1.6', author='Baruffaldi', title='test', subject='no subject declared', keywords='test'):
		# todo: deve gestire un numero variabile di elementi ( /Contents)
		self.ver = ver
		self.author = author
		self.title = title
		self.subject = subject
		self.keywords = keywords
		self.l = []
		self.info_obj_idx = False  # doc'è l'oggetto delle info sul file
		self.obj_idx = 0
		# [1] Catalogo
		self.pages = []
		self.page_objects = []
		self.add_dz('Catalog', ['Outlines', 2, 'Pages', 3], to_page=False)
		# [2] Outlines
		self.add_dz('Outlines', ['Count', '0'], to_page=False)
		# [3] l'oggetto 3 è il raccoglitore di pagine
		self.add_dz('Pages', ['Kids', '[%($pages$)s]' , 'Count', '%($len(pages)$)s'], to_page=False)
		# [4] "pdf"
		self.add_obj("[/PDF]", to_page=False)
		# [5] un primo font
		self.add_dz('Font', ['Subtype', 'Type1', 'Name', 'F1', 'BaseFont', 'Helvetica', 'Encoding', 'MacRomanEncoding'], to_page=False)
		# [6] info object
		self.info_obj_idx = self.add_info_obj()
		self.add_page()

	def add_obj(self, txt, raw=False, to_page = True):
		if raw:
			self.l.append("\t" + txt)
		else:
			self.l.append("\t" + txt.replace("\t", "").replace('\n', '\n\t'))
		self.obj_idx += 1
		if to_page:
			self.page_objects[-1].append(self.obj_idx)
		return self.obj_idx

	def add_page(self):
		idx = self.add_obj("""<< /Type /Page
				/Parent 3 0 R
				/MediaBox [0 0 612 792] 
				/Contents [%($page_objects$)s]
				/Resources << /ProcSet 4 0 R 
					/Font << /F1 5 0 R >>
					>>
				>>""", False, to_page=False)
		self.pages.append(idx)
		self.page_objects.append([])
		return idx

	def add_dz(self, tipo, sequenza, to_page=True):
		return self.add_obj(pdf_dz(tipo, sequenza), to_page=to_page)

	def add_txt_obj(self, txt, x, y, fontSize=12, pdf_style=''):
		# todo: non calcola la lunghezza delle stringhe
		if pdf_style:
			extra_pdf = '\n%s\n' % pdf_style
		else:
			extra_pdf = ''
		stream1 = """BT
/F1 %s Tf
%s %s Td%s 
(%s) Tj
ET""" % (fontSize, x, 792 - y, extra_pdf, txt)
		new_id = self.add_obj("<< /Length %s >>\nstream\n%s\nendstream" % (len(stream1), stream1), raw=True)
		return new_id
		#self.page_objects[-1].append(new_id)

	def add_stream(self,stream1):
		new_id = self.add_obj("<< /Length %s >>\nstream\n%s\nendstream" % (len(stream1), stream1), raw=True)
		return new_id

	def add_info_obj(self):
		"""
		Title
		Author
		Subject
		Keywords
		Creator = pdffino.py
		Producer = pdffino.py
		CreationDate = (D:YYYYMMDDHHmmSSOHH' mm)
		"""
		timestamp = time.time()
		data_s = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d%H%M%S')
		print(data_s)
		l = [
			'Title', pdf_str('documento di test'),
			'Author', pdf_str(self.author),
			'Subject', pdf_str(self.subject),
			'Keywords', pdf_str(self.keywords),
			'Creator', pdf_str('pdffino.py'),
			'Producer', pdf_str('pdffino.py'),
			'CreationDate', pdf_str("D:%s" % data_s)
		]
		return self.add_dz('Info', l,to_page= False)

	def __str__(self):

		txt = "%%PDF-%s\n" % self.ver
		xref_l = [0]
		# --- Objects
		n_chr = 0
		pagina = 0
		for n in range(1,len(self.l)+1):
			xref_l.append(len(txt))
			txt += "%s 0 obj\n" % n
			if '$pages$' in self.l[n - 1]:
				d = {'$pages$': " ".join(["%s 0 R" % x for x in self.pages]),
					 "$len(pages)$": '%s' % len(self.pages)}
				txt += self.l[n - 1] % d
			elif '$page_objects$' in self.l[n - 1]:
				# todo: migliorare
				d = {'$page_objects$': " ".join(["%s 0 R" % x for x in self.page_objects[pagina]])}
				pagina += 1
				txt += self.l[n - 1] % d
			else:
				txt += self.l[n - 1]
			txt += "\nendobj\n\n"
		# --- File Structure (of Objects)
		xref_pos = len(txt)
		txt += "xref\n0 %s\n" % (n + 1)  # gli oggetti sono numerati da 0 a el+1
		txt += "0000000000 65535 f\n"
		for xref1 in xref_l:
			txt += "%010d 00000 n\n" % xref1
		txt += "trailer\n"
		txt += "\t<< /Size %s\n" % (n + 1)
		txt += "\t/Root 1 0 R\n"
		if self.info_obj_idx:
			txt += "\t/Info %s 0 R\n" % self.info_obj_idx
		txt += "\t>>\n"
		txt += "startxref\n"
		txt += "%s\n" % xref_pos
		txt += "%%EOF"
		return txt

	def xref_read(self):
		text = str(self)
		xref_ini = int(text.splitlines()[-2])
		print('xref position is =', xref_ini)
		print(text[xref_ini:xref_ini + 4])
		return True

	def save_file(self, filename):
		f1 = open(filename, 'w')
		f1.write(str(self))
		f1.close()
		return True

	def paragraph(self, txt, x, y, dy):
		n = 0
		for riga in txt.splitlines():
			self.add_txt_obj(riga.strip(), x, y + n * dy)
			n += 1
		return n


#####

def md2pdf(pdf_obj, testo, min_x=25, min_y=25):
	"""
	Markdown converter

	only headers
	"""
	tot_y = 0
	for riga in testo.splitlines():
		header = False
		if riga.startswith('#' * 5):
			stile = S_GREY
			dy += 26
		elif riga.startswith('#' * 4):
			stile = S_NORMAL
			dy += 22
		elif riga.startswith('#' * 3):
			stile = S_STROKE
			dy += 18
		elif riga.startswith('#' * 2):
			stile = S_GREY
			dy += 16
		elif riga.startswith('#'):
			stile = S_NORMAL
			dy += 14
		else:
			stile = S_NORMAL
			dy = 12
		if (tot_y + dy * 1.4) > A4HEIGHT:
			pdf_obj.add_page()
			tot_y = 0
		pdf_obj.add_txt_obj(riga, min_x, min_y + tot_y + dy, dy, stile)
		tot_y += dy * 1.4
	return True


def test1():
	"""
	una pagina, pià stringhe di testo
	:return:
	"""
	test1 = PDF()
	test1.add_txt_obj('ciao', 100, 100)
	test1.add_txt_obj('ciao ancora', 200, 200)
	test1.xref_read()
	f1 = open('pdffino_test1.pdf', 'w')
	f1.write(str(test1))
	f1.close()


def test2():
	"""

	:return:
	"""
	test2 = PDF()
	testo = __doc__
	test2.paragraph(testo, 100, 200, 20)
	test2.save_file('pdffino_test2.pdf')


def test3():
	test3 = PDF()
	test3.add_txt_obj('ciao', 100, 100, 20, S_GREY)
	test3.add_txt_obj('ciao ancora', 200, 200, 30, S_STROKE)
	test3.save_file('pdffino_test3.pdf')


def test4():
	"""
	metodo Markdown semplificato: solo paragrafi e titoli
	:return:
	"""
	test2 = PDF()
	md2pdf(test2, __doc__)
	test2.save_file('pdffino_test4.pdf')


def test5():
	"""
	test di pdfinfo
	:return:
	"""
	test5 = PDF(title='test n.5: file attributes', keywords='pdffinfo.py test info',
				subject="example with info object defined", author='baruffaldi.p@gmail.com')
	test5.add_txt_obj(test5.title, 100, 100, 20, S_GREY)
	test5.add_txt_obj('dizionario di informazioni visibili dai file browser', 20, 200, 10, S_NORMAL)
	test5.save_file('pdffino_test5.pdf')


def test6():
	t1 = PDF(title='test n.6: multiple pages', keywords='pdffino.py pages',
			subject="more that one page",
			author='baruffaldi.p@gmail.com')
	t1.add_txt_obj(t1.title, 20, 40, 30, S_STROKE)
	dx = 20
	tot_x = 0
	for pag in range(1,10):
		for n in range(10):
			tot_x+= dx
			t1.add_txt_obj('row n. %s' % (n+pag*10), 12, 50 + tot_x, 12, S_NORMAL)
		t1.add_page()
		tot_x = 0
	t1.save_file('pdffino_test6.pdf')

def test7():
	t1 = PDF(title='test n.7: elemento ripetuto', keywords='pdffino.py pages',
			subject="more that one page",
			author='baruffaldi.p@gmail.com')
	titolo = t1.add_txt_obj(t1.title, 20, 40, 30, S_STROKE)
	dx = 20
	tot_x = 0
	for pag in range(1,10):
		if pag > 1:
			t1.add_page()
			tot_x = 0
			t1.page_objects[-1].append(titolo)
		for n in range(10):
			tot_x+= dx
			t1.add_txt_obj('row n. %s' % (n+pag*10), 12, 50 + tot_x, 12, S_NORMAL)

	t1.save_file('pdffino_test7.pdf')


def test8():
	t1 = PDF(title='test n.8: grafica', keywords='pdffino.py graphics',
			subject="graphics",
			author='baruffaldi.p@gmail.com')
	t1.add_txt_obj('Graphics', 50, 50)
	t1.add_stream('1.0 0.0 0.0 RG\n 100 720 m\n 200 720 l\n S')
	t1.save_file('pdffino_test8.pdf')




####### Trash zone
'''
def add_info_obj(self):
		txt = "/Title (PDFFINO1)\n"
		txt += "/Creator (Paolo Baruffaldi)\n"
		txt += "/Producer (Baruffaldi's pdffino.py)\n"
		txt += "/CreationDate (D: 20201006204500)\n"
		self.info_obj_idx = len(self.l) + 1

def trash():
	pass
	# self.add_obj("""<< /Type /Catalog
	# /Outlines 2 0 R
	# /Pages 3 0 R
	# >>""")
	#self.add_obj("""<< /Type /Outlines
	#/Count 0
	#>>""")
	# self.add_obj("""<< /Type /Pages
	# /Kids [4 0 R]
	# /Count 1 >>""")
	self.add_obj("""<< /Type /Font
		/Subtype /Type1
		/Name /F1
		/BaseFont /Helvetica
		/Encoding /MacRomanEncoding
		>>""")
'''
#self.add_obj("""<< /Type /Page
		#/Parent 3 0 R
		#/MediaBox [0 0 612 792]
		#/Contents [%($page_objects0$)s]
		#/Resources << /ProcSet 5 0 R
		#	/Font << /F1 6 0 R >>
		#	>>
		#>>""", to_page=False)

def test():
	test1()
	test2()
	test3()
	test4()
	test5()
	test6()
	test7()
	test8()

if __name__ == "__main__":
	main_cli()
