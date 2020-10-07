# locust

Track changes to Python source code across git refs.

## Dependencies

### pygit2

Follow `pygit2` installation instructions: https://www.pygit2.org/install.html

### Run
```
> locust -r ~/simiotics/spire/ -i master -t bug-3-spire-groups | jq . | less
```
