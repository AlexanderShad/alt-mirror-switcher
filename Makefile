PREFIXBIN=/usr/bin
SHAREDIR =/usr/share
NAME=alt-mirror-switcher

install: install-data install-bin

install-data:
	install -d $(SHAREDIR)/$(NAME)
	install -d $(SHAREDIR)/applications
	cp -a $(NAME).py $(SHAREDIR)/$(NAME)
	cp -a $(NAME).desktop $(SHAREDIR)/applications

install-bin:
	install -Dm755 $(NAME) $(PREFIXBIN)/$(NAME)
