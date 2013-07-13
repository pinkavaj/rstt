all:
	echo "Use: make check localinstall"
	false

check:
	cd grc_gnuradio && for f in qa_*.py; do python2 $${f} || exit 1; done

localinstall:
	cp -r grc_gnuradio/rstt_*.py grc_gnuradio/rstt_*.py.xml ~/.grc_gnuradio
