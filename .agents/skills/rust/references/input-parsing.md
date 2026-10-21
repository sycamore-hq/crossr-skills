# Input parsing

Parse at the edge. The core never sees wire types.

## Rules

RP-01  Parse wire values into domain newtypes at the adapter edge. Do not validate later. Naked `String` / `&str` must not cross into the core.

RP-02  Newtypes that wrap wire input are constructed at the edge, not deep in the core.

RP-03  Invalid input dies at the parse boundary. The core receives a domain value or nothing.

RP-04  A closed set of wire strings (method names, tool names, CLI flags, kinds, modes like `"off"`) is parsed into an enum with an `Unknown(String)` variant at the point of extraction — `#[serde(from = "String")]` or one `From<String>` / `FromStr`. String-literal `match` arms appear only inside that impl; handlers match on the enum.
       check: rg '^\s*"[^"]*"\s*(\|\s*"[^"]*"\s*)*=>' --glob '*.rs' → every hit is inside a `From<String>` / `FromStr` impl

## How

A string from HTTP, a CLI flag, or a JSON field is not a `UserId`. Parse it into a newtype in the adapter (New Type pattern: wrap the primitive so the core cannot be handed a raw string):

```rust
impl UserId {
    pub fn parse(raw: &str) -> Result<Self, ParseError> { /* … */ }
}

fn handle(req: Request) -> Result<Response, GatewayError> {
    let id = UserId::parse(&req.path_id)?;
    Ok(service.get(id)?.into())
}
```

A handler is an adapter, but that does not license `match s.as_str()` anywhere in it. Convert at extraction and keep the unknown value for the error:

```rust
#[derive(Deserialize)]
#[serde(from = "String")]
enum Method { Initialize, ToolsCall, Unknown(String) }

impl From<String> for Method {
    fn from(s: String) -> Self {
        match s.as_str() {
            "initialize" => Self::Initialize,
            "tools/call" => Self::ToolsCall,
            _ => Self::Unknown(s),
        }
    }
}

fn dispatch(method: Method) -> Result<Value, RpcError> {
    match method {
        Method::Initialize => initialize(),
        Method::ToolsCall => call(),
        Method::Unknown(m) => Err(RpcError::MethodNotFound(m)),
    }
}
```

Core signatures take `UserId`, `Email`, `TenantId` — not `String`. Stringly types that leak past the edge become boolean flags and sentinel checks in the core. Kill them at the door.
