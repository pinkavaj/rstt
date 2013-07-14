INSTALL_DST=~/.grc_gnuradio/rstt

all:
	echo "Use: make check localinstall"
	false

check:
	cd src/rstt && for f in qa_*.py; do python2 $${f} || exit 1; done

localinstall:
	mkdir -p $(INSTALL_DST)
	cp src/rstt/__init__.py	$(INSTALL_DST)
	cp src/rstt/symbols2bites.py $(INSTALL_DST)
	cp src/rstt/symbols2bites.py.xml $(INSTALL_DST)
	cp src/rstt/bites2bytes.py $(INSTALL_DST)
	cp src/rstt/bites2bytes.py.xml $(INSTALL_DST)
	cp src/rstt/bytes2frames.py $(INSTALL_DST)
	cp src/rstt/bytes2frames.py.xml $(INSTALL_DST)
	grcc src/rstt/decode.grc
