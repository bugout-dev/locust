# Locust docker images

## Building

To build a `locust` docker image, use the [build script](./build.sh):

```
./build.sh
```

This builds an image with the current state of the locust code base and gives it two tags:

1. `latest`
2. `t-<UTC time of build in the format YYYYmmdd-HHMM>`

You can set additional tags from the command line. For example, to add the `foo` and `bar` tags:

```
./build.sh foo bar
```

You do not need to call the build script from this directory. For example, you can call it from the
root directory of this repo:

```
docker/build.sh
```

## Running

To see the `locust` help message:

```
docker run --rm bugout/locust
```

If you have a git repository that you would like to run locust on:

```
docker run \
    -v <absolute path to repo root>:/usr/src/app \
    bugout/locust \
    -r /usr/src/app <initial git ref> <terminal git ref> --format yaml
```
