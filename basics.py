#!/bin/python

"""
hier fasse ich nuetzliche basiselemente fuer python zusammen
Dies ist uebrigens ein mehrzeiliger Kommentar
"""

# Basics for python
spam = 1
string = "# Dies ist ein Kommentar"
x = y = z = 0
a,b = 1,2

print x
print("""\
Dies ist eine lange ausgabe
Mehr Mehr!
""")

# Strings
word = "moin "*2
word[0:4] + " " + word[0:4]
len(word);

# Listen
l = ["spam", "eggs", 100, 1234]
l[0:2] = [1, 12]
l[0:2] = []
l.append("ende")


# Letzter Wert: _

# Typumwandlung
str(x);
float(x);

# Konditionalabfragen
if x < 0:
    x = 0
    print "x ist kleiner 0"
elif x == 0:
    print "x ist 0"
else:
    print "oder doch nicht?"

"""
SCHLEIFEN
"""
# while
a,b=0,1
while b < 10:
    print(b)
    a, b  = b, a+b

# for
a = ['Katze', 'Fenster', 'rauswerfen']
for x in a:
    print(x, len(x))

# for - iterator
for i in range(len(a)):
    print(i, a[i]);



# Rechnen
7 // 3 # Ganzzahldivision

# Mathe
cplx = complex(1,1)
cplx = 1 + 1j
cplx.real
cplx.imag
abs(cplx)
