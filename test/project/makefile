REPO=repo
INDEX=$(REPO)/index

DDD=~/workspace/ddd/ddd.py

$(INDEX)/ModuleA: ModuleA/ModuleA.ddd
	python $(DDD) add ModuleA/ModuleA.ddd $(REPO)
$(INDEX)/SubmoduleB: ModuleB/ModuleB_sub.ddd
	python $(DDD) add ModuleB/ModuleB_sub.ddd $(REPO)
$(INDEX)/ModuleB: ModuleB/ModuleB.ddd $(INDEX)/SubmoduleB
	python $(DDD) add ModuleB/ModuleB.ddd $(REPO)
$(INDEX)/projectxx: project.ddd $(INDEX)/ModuleB $(INDEX)/ModuleA
	python $(DDD) add project.ddd $(REPO)

project_check: $(INDEX)/projectxx
	python $(DDD) check projectxx $(REPO)

clean:
	rm $(INDEX)/*