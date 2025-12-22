PREFIXBIN=/usr/bin
SHAREDIR =/usr/share
NAME=alt-mirror-switcher

install: install-data install-bin

install-data:
	install -d $(SHAREDIR)/$(NAME)
	install -d $(SHAREDIR)/applications
	cp -a *.py $(SHAREDIR)/$(NAME)
	cp -a $(NAME).desktop $(SHAREDIR)/applications
	cp -p -r locale $(SHAREDIR)
	cp -p -r mirrors $(SHAREDIR)/$(NAME)

install-bin:
	install -Dm755 $(NAME) $(PREFIXBIN)/$(NAME)
	install -Dm755 ams $(PREFIXBIN)/ams
	