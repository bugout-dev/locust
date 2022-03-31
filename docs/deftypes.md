# Locust definition types

Locust represents changes that it is aware of as `RawDefinition` objects, which are defined by
the following protobuf message (see [`parse.proto`](../protobuf/parse.proto) for up-to-date definition of the message):

```
message RawDefinition {
    string name = 1;
    string change_type = 2;
    int32 line = 3;
    int32 offset = 4;
    int32 end_line = 5;
    int32 end_offset = 6;
    DefinitionParent parent = 7;
}
```

The `change_type` field defines what kind of abstraction the `RawDefinition` refers to.

To maintain consistency across programming languages, there is a common set of values for `change_type`
that most programming languages can implement. Of course, specific plugins can choose to introduce
new types (which is why the `change_type` field is of type `string` rather than an enumeration).

The common values for `change_type` are:
1. `function` - represents a function definition
2. `async_function` - represents an asynchronous function definition (useful in languages like Python and Javascript)
3. `class` - represents a class definition
4. `method` - method in a class
5. `dependency` - represents a dependency being defined/imported
6. `usage` - represents invocation of a function, instantiation of a class, etc.

## Defition type support in Locust Plugins

### Python

Locust's Python analyzer supports the following definitions:
1. `function`
2. `async_function`
3. `class`
4. `dependency`
5. `usage`

### Javascript

Locust's Javascript analyzer supports the following definitions:
1. `function`
2. `class`
3. `method`

It also supports the following custom definitions:
1. `component` - a JSX component (e.g. in React code)
