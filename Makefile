PWD := $(shell pwd)

compile-proto:
	mkdir -p protogen
	protoc --pyi_out=$(PWD)/protogen -I=$(PWD)/proto --python_out=$(PWD)/protogen $(PWD)/proto/*