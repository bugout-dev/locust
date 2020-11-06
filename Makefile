.PHONY: test docker protogen

# Requires LOCUST_TESTCASES_DIR environment variable to be set.
test:
	./test.sh

# Run with LOCUST_DOCKER_PUSH=true to push images to Docker Hub.
docker:
	docker/build.sh $(ARGS)

protogen: locust/git_pb2.py locust/parse_pb2.py locust/git_pb2.pyi locust/parse_pb2.pyi

locust/git_pb2.py:
	protoc -Iprotobuf/ --python_out=locust/ protobuf/git.proto

locust/git_pb2.pyi:
	protoc -Iprotobuf/ --mypy_out=locust/ protobuf/git.proto

locust/parse_pb2.py:
	protoc -Iprotobuf/ --python_out=locust/ protobuf/parse.proto
	sed -i -e 's/import git_pb2/from \. import git_pb2/g' locust/parse_pb2.py

locust/parse_pb2.pyi:
	protoc -Iprotobuf/ --mypy_out=locust/ protobuf/parse.proto
	sed -i -e 's/from git_pb2 import /from \.git_pb2 import/g' locust/parse_pb2.pyi

build dist bugout_locust.egg-info:
	python setup.py sdist bdist_wheel

clean:
	rm -f locust/*_pb2.py
	rm -f locust/*_pb2.pyi
	rm -rf dist/ build/ bugout_locust.egg-info/
