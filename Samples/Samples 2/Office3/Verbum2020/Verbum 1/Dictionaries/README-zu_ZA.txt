How to use this dictionary framework
====================================

Each dictionary has its own directory using the ISO639 language code.  Eg
Afrikaans uses af.  In each directory is an aspell, myspell and in some cases
an ispell directory - these contain the speller specific information.

Files and directories
---------------------

|-- Makefile
|-- af
|   |-- COPYING
|   |-- CREDITS
|   |-- ChangeLog
|   |-- INSTALL
|   |-- Makefile
|   |-- README
|   |-- VERSION
|   |-- aspell
|   |   |-- Copyright
|   |   |-- info.in
|   |-- ispell
|   |   |-- README
|   |   `-- afrikaans.aff
|   |-- myspell
|   |   |-- README_af_ZA.txt
|   |   |-- af_ZA.aff
|   |-- wordlists
|   |   |-- wordlist.nieuwoudt.in

Prerequisites
============
aspell - needs prezip-bin (since 0.60, was word-list-compress for 0.50), 
which is contained in the aspell package for your system. Other tools 
needed to package and build are located in the utils directory

myspell - the tools needed are in the utils directory


Required Files
==============

ispell
------
The framework can build ispell but it is disabled by default because we are not
completely sure how to build ispell dictionaries.

aspell
------
Copyright - details of the copyright holders etc.  The actual copyright text
is added based on a line in the info.in file.
info.in - some basic definitions for the aspell package including copyright
holders, license, language name etc.
lang.dat - the language data file, used along with info.in.
What can be problematic in the language data file is the "special" line:
	special ' **- - -*- 4 -*- 6 -*-
It is simple to understand.  The above says ' (apostrophe) is permissible at the
beginning of a word and the middle. - (dash) is allowed in the middle of a
word, etc
Check the Afrikaans one for a good understanding of its construction.  If 
you need more details then look at the README instructions in the latest 
aspell dictionary build system (the aspell-lang package):
	ftp://ftp.gnu.org/gnu/aspell/aspell-lang-20071024.tar.bz2

myspell
-------
README_lang_REGION.txt - a README containing Copyright info and installation
instructions.
lang_REGION.aff - the affix file.  Mostly these are based on ispell affix
compression.  Follow the instructions ?here? for converting an ispell affix file
to myspell.  An affix file allows you to compress a wordlist and expand it to
the exact same set of words.  If you have not developed affix rules for the
language then the minimum you need is a SET and TRY line.

SET - the character set used by the language.  Only ISO8859 character sets can
be used in MySpell.  Although I think you can define your own internal mapping
if your language does not match an ISO charset. (Need to confirm this)
TRY - a list of letters in order of frequency.  The python script 
src/wordlist/letter-frequency.py allows you to create a frequency list.

Other useful entries:
MAP - map similar characters eg eêë
REP - create REPlacement maps that are useful for mapping common spelling
mistakes. eg REP ph f - as in phone.

Affix compression:
SFX - a suffix
PFX - a prefix
FIXME add more details on creating these.

Setting up a new language
-------------------------
Apart from input files required by each of the different spellcheckers, as
listed above, the main requirements are a wordlist and some definitions in the
language Makefile.

The wordlist is simply a text list of words one per line - currently we store these in UTF-8 to
ensure ease of use in the future.  Lines that start with a # are treated as
comments and removed when the wordlist is processed.  The wordlists can be
called anything although we name them wordlist.*.in.  But as you list them in
the Makefile you can name them as you please.  We have kept existing wordlists
in tact and used separate files for new additions.  In English we have grouped
similar concepts together eg. bird names, city names, etc.  Some languages
group words according to parts of speech which may aid later use with advances
in grammar checkers or in agglutinative languages that may have rules as to how
words may be joined together.

The Makefile calls the generic Makefile called utils/Makefile.language.  The
language Makefile contains a number of definitions such as the name of the
language its character set, etc.  If you need to understand some of the build
process steps then look at the generic Makefile.

Add a VERSION file.  We default to using the date as spellcheckers are really
enhancements and refinements of wordlists, so a newer date should always
indicate a better spellchecker.

Also add you language to the Makefile in the dict/ directory.  Both as a build
rule and as a TARGET.


Building
--------

make - generate all dictionaries for that language
make count - will return simple stats on your wordlist
make aspell - create the aspell dictionary (relatively quick)
make myspell - create a myspell dictionary (looooong)
make clean - cleans up all packaged files

Outputs
-------
All outputs are placed in the respective spellchecker directories.

aspell - creates a tarball that would be compiled and installed on the target platform

myspell - creates a few outputs.  
	lang_REGION.zip - the basic MySpell spellchecker usable in OpenOffice.org
	pack-lang_REGION.xip - as above but installable by the offline installer
	lang-REGION.xpi - the same as lang_REGION.zip but installable in Mozilla

Resources - South African
-------------------------

Common Names of fish - http://www.fishbase.org/search.cfm
Birds - 
	Robert's Birds list - http://web.uct.ac.za/depts/fitzpatrick/docs/listintro.html
	http://www.wildlifesafari.info/south_african_birds.htm
	http://www.wildlifesafari.info/southern_africa_bird_checklist.htm
Trees - http://www.wildlifesafari.info/southern_africa_tree_list.html
Endangered species -
http://www.unep-wcmc.org/index.html?http://sea.unep-wcmc.org/isdb/CITES/Taxonomy/?displaylanguage=eng~main
http://www.e-gnu.com/check_005.html
http://www.e-gnu.com/check_003.html
http://www.e-gnu.com/check_004.html
Listed companies:
http://www.jse.co.za/listed/companies/la.html
Names Changes:
http://africanhistory.about.com/cs/southafrica/a/sa_new_name.htm
www.sapo.co.za - get downloadable postal codes for names of towns and suburbs
