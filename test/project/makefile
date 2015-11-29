REPO=repo
INDEX=$(REPO)/index
SOURCE=sources

DDD=~/workspace/ddd/ddd.py

repo:
	python $(DDD) init repo

source:
	mkdir $(SOURCE)

$(INDEX)/ModuleA: ModuleA/ModuleA.ddd repo
	python $(DDD) add ModuleA/ModuleA.ddd $(REPO)
$(INDEX)/SubmoduleB: ModuleB/ModuleB_sub.ddd repo
	python $(DDD) add ModuleB/ModuleB_sub.ddd $(REPO)
$(INDEX)/ModuleB: ModuleB/ModuleB.ddd $(INDEX)/SubmoduleB repo
	python $(DDD) add ModuleB/ModuleB.ddd $(REPO)
$(INDEX)/projectxx: project.ddd $(INDEX)/ModuleB $(INDEX)/ModuleA repo
	python $(DDD) add project.ddd $(REPO)

$(SOURCE)/ModuleA_decl.h:$(INDEX)/ModuleA project_check source
	python $(DDD) export ModuleA --template decl.h --output $(SOURCE)/ModuleA_decl.h repo
$(SOURCE)/ModuleB_decl.h:$(INDEX)/ModuleB project_check source
	python $(DDD) export ModuleB --template decl.h --output $(SOURCE)/ModuleB_decl.h repo
$(SOURCE)/SubmoduleB_decl.h:$(INDEX)/SubmoduleB project_check source
	python $(DDD) export SubmoduleB --template decl.h --output $(SOURCE)/SubmoduleB_decl.h repo
$(SOURCE)/projectxx_def.c:$(INDEX)/projectxx project_check source
	python $(DDD) export projectxx --template def.c --output $(SOURCE)/projectxx_def.c repo


export_sources:$(SOURCE)/ModuleA_decl.h $(SOURCE)/ModuleB_decl.h $(SOURCE)/SubmoduleB_decl.h $(SOURCE)/projectxx_def.c
	echo hallo

project_check: $(INDEX)/projectxx
	python $(DDD) check projectxx $(REPO)
	touch project_check

build.txt: $(INDEX)/projectxx
	if ! test -f build.txt; then echo 0 > build.txt; fi
	echo $$(($$(cat build.txt) + 1)) > build.txt

commit: project_check build.txt
	python $(DDD) commit projectxx --message "autocommit" --tag $$(cat build.txt) $(REPO)

view:
	python $(DDD) view $(REPO)
	xdg-open viewer.html
    
view_project: $(INDEX)/projectxx
	python $(DDD) view projectxx $(REPO)
	explorer viewer.html

clean:
	rm -rf $(REPO)
	rm build.txt