PWD := $(shell pwd)

compile-proto:
	@mkdir -p protogen
	@protoc --pyi_out=$(PWD)/src/magplan/protogen -I=$(PWD)/proto --python_out=$(PWD)/src/magplan/protogen $(PWD)/proto/*