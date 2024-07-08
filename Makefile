SPECIES = human mouse

human_LISTS = transcription_factor
mouse_LISTS = transcription_factor

.PHONY: all
.PHONY: complete
.PHONY: namespaces
.PHONY: lists

all: complete namespaces lists

clean:
	rm -rf `find . -name 'log.txt'`


define SPECIES_RULES

complete: $(1)_complete

namespaces: $(1)_namespaces

.PHONY: $(1)_complete
$(1)_complete: genes/$(1)/namespaces/log.complete.txt

genes/$(1)/namespaces/log.complete.txt: scripts/complete_namespaces.py | $(wildcard genes/$(1)/namespaces/sources/*.Missing.tsv)
	set -o pipefail && scripts/complete_namespaces.py $(1) 2>&1 | tee genes/$(1)/namespaces/log.complete.txt

.PHONY: $(1)_namespaces
$(1)_namespaces: genes/$(1)/namespaces/log.txt

genes/$(1)/namespaces/log.txt: scripts/compute_namespaces.py \
    $(filter-out %.Missing.tsv,$(filter-out README.md,$(wildcard genes/$(1)/namespaces/sources/*)))
	set -o pipefail && scripts/compute_namespaces.py $(1) 2>&1 | tee genes/$(1)/namespaces/log.txt
	rm genes/$(1)/namespaces/log.complete.txt

.PHONY: $(1)_lists
lists: $(1)_lists

$(1)_lists: genes/$(1)/lists/log.txt

$(foreach list,$($(1)_LISTS),$(eval $(call SPECIES_LIST_RULES,$(1),$(list))))
endef


define SPECIES_LIST_RULES

genes/$(1)/lists/log.txt: genes/$(1)/lists/$(2)/log.txt

genes/$(1)/lists/$(2)/log.txt: scripts/compute_list.py genes/$(1)/namespaces/log.txt \
    $(filter-out %.Missing.tsv,$(filter-out README.md,$(wildcard genes/$(1)/lists/$(2)/sources/*)))
	set -o pipefail && scripts/compute_list.py $(1) $(2) 2>&1 | tee genes/$(1)/lists/$(2)/log.txt
endef


$(foreach species,$(SPECIES),$(eval $(call SPECIES_RULES,$(species))))
