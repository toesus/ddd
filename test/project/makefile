REPO=repo
INDEX=$(REPO)/index
SOURCE=source

ifeq ($(OS),Windows_NT)
    DDD=c:/git/ddd/ddd.py
    EXPLORER_CMD = explorer
else
    DDD=~/workspace/ddd/ddd.py
    EXPLORER_CMD = xdg-open
endif
repo:
	python $(DDD) init repo

source:
	mkdir $(SOURCE)

$(REPO)/project.ddd:ModuleA/ModuleA.ddd ModuleB/ModuleB.ddd config.ddd $(REPO)
	python $(DDD) check ModuleA/ModuleA.ddd ModuleB/ModuleB.ddd --config config.ddd --output $(REPO)/project.ddd $(REPO)

$(SOURCE)/ModuleA_decl.h:ModuleA/ModuleA.ddd config.ddd source
	python $(DDD) export ModuleA/ModuleA.ddd --config config.ddd --template decl.h --output $(SOURCE)/ModuleA_decl.h repo
$(SOURCE)/ModuleB_decl.h:ModuleB/ModuleB.ddd config.ddd source
	python $(DDD) export ModuleB/ModuleB.ddd --config config.ddd --template decl.h --output $(SOURCE)/ModuleB_decl.h repo
$(SOURCE)/project_def.c: $(REPO)/project.ddd source
	python $(DDD) export $(REPO)/project.ddd --config config.ddd --template def.c --output $(SOURCE)/project_def.c repo

$(SOURCE)/conditions.dummy: $(INDEX)/projectxx
	python $(DDD) export project/projectxx --template conditions.json --output $(SOURCE)/conditions.dummy repo
$(SOURCE)/conditions.json: $(SOURCE)/conditions.dummy
	dcc $(SOURCE)/conditions.dummy -P -o $(SOURCE)/conditions.json

build.txt: $(REPO)/project.ddd
	if ! test -f build.txt; then echo 0 > build.txt; fi
	echo $$(($$(cat build.txt) + 1)) > build.txt

commit:$(SOURCE)/ModuleA_decl.h $(SOURCE)/ModuleB_decl.h $(SOURCE)/project_def.c build.txt
	python $(DDD) commit $(REPO)/project.ddd --message "autocommit" --tag $$(cat build.txt) $(REPO)

view:
	python $(DDD) view $(REPO)
	$(EXPLORER_CMD) viewer.html

clean:
	rm -rf $(REPO)
	rm -rf $(SOURCE)
	rm build.txt
