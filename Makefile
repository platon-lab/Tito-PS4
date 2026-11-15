TC ?= $(OO_PS4_TOOLCHAIN)
EBOOT_TOOL := $(or $(shell command -v create-eboot 2>/dev/null),$(shell find $(TC) -name create-eboot -type f 2>/dev/null | head -n 1))
PKGTOOL := $(or $(shell command -v PkgTool.Core 2>/dev/null),$(TC)/bin/linux/PkgTool.Core)
CC := clang
LD := ld.lld
CFLAGS := --target=x86_64-pc-freebsd12-elf -fPIC -funwind-tables -fno-builtin -c -isysroot $(TC) -isystem $(TC)/include
LDFLAGS := -m elf_x86_64 -pie --script $(TC)/link.x --eh-frame-hdr -L$(TC)/lib
LIBS := -lc -lkernel -lSceUserService -lScePad -lSceSysmodule
OBJS := main.o

all: eboot.bin

%.o: %.c
	$(CC) $(CFLAGS) -o $@ $<

tito.elf: $(OBJS)
	$(LD) $(LDFLAGS) $(TC)/lib/crt1.o $(OBJS) $(LIBS) -o $@

eboot.bin: tito.elf
	$(if $(EBOOT_TOOL),,$(error create-eboot не найден в $(TC)))
	sh make_eboot.sh $(EBOOT_TOOL)
	test -s eboot.bin

pkg: eboot.bin
	python3 make_pkg_files.py
	$(PKGTOOL) pkg_build pkg/pkg.gp4 .

clean:
	rm -rf *.o tito.elf tito.oelf eboot.bin pkg sce_sys *.pkg

.PHONY: all pkg clean
