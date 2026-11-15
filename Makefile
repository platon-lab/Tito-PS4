TC ?= $(OO_PS4_TOOLCHAIN)
TOOLS := $(TC)/bin/linux
CC := clang
LD := ld.lld
CFLAGS := --target=x86_64-pc-freebsd12-elf -fPIC -funwind-tables -fno-builtin -c -isysroot $(TC) -isystem $(TC)/include
LDFLAGS := -m elf_x86_64 -pie --script $(TC)/link.x --eh-frame-hdr -L$(TC)/lib
LIBS := -lkernel -lSceUserService -lScePad -lSceSysmodule
OBJS := main.o

all: eboot.bin

%.o: %.c
	$(CC) $(CFLAGS) -o $@ $<

tito.elf: $(OBJS)
	$(LD) $(LDFLAGS) $(TC)/lib/crt1.o $(OBJS) $(LIBS) -o $@

eboot.bin: tito.elf
	$(TOOLS)/create-fself -in tito.elf -out tito.oelf -eboot eboot.bin -paid 0x3800000000000011

pkg: eboot.bin
	python3 make_pkg_files.py
	$(TOOLS)/PkgTool.Core pkg_build pkg/pkg.gp4 .

clean:
	rm -rf *.o tito.elf tito.oelf eboot.bin pkg sce_sys *.pkg

.PHONY: all pkg clean
