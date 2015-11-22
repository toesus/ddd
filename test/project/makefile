REPO=repo
INDEX=$(REPO)/index

DDD=~/workspace/ddd/ddd.py

repo:
	python $(DDD) init repo

$(INDEX)/ModuleA: ModuleA/ModuleA.ddd repo
	python $(DDD) add ModuleA/ModuleA.ddd $(REPO)
$(INDEX)/SubmoduleB: ModuleB/ModuleB_sub.ddd repo
	python $(DDD) add ModuleB/ModuleB_sub.ddd $(REPO)
$(INDEX)/ModuleB: ModuleB/ModuleB.ddd $(INDEX)/SubmoduleB repo
	python $(DDD) add ModuleB/ModuleB.ddd $(REPO)
$(INDEX)/projectxx: project.ddd $(INDEX)/ModuleB $(INDEX)/ModuleA repo
	python $(DDD) add project.ddd $(REPO)

project_check: $(INDEX)/projectxx
	python $(DDD) check projectxx $(REPO)

build.txt: $(INDEX)/projectxx
	if ! test -f build.txt; then echo 0 > build.txt; fi
	echo $$(($$(cat build.txt) + 1)) > build.txt

commit: project_check build.txt
	python $(DDD) commit projectxx --message "autocommit" --tag $$(cat build.txt) $(REPO)

view:
	python $(DDD) view $(REPO)
	xdg-open viewer.html

clean:
	rm -rf $(REPO)
	rm build.txt