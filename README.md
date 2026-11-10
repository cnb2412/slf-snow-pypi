# slf-snow

> **Work in progress:** This package is under development. It is not yet
> published on PyPI and has no usable API yet.

`slf-snow` will be an asynchronous Python client for the public
[measurement API](https://measurement-api.slf.ch/) of the WSL Institute for
Snow and Avalanche Research SLF. It provides current snow values (snow height,
new snow, water equivalent of new snow) from SLF study plots and IMIS stations
as typed Python objects, with a small, well-defined set of errors. It is built
for asynchronous consumers such as Home Assistant integrations.

This is an independent project and is not affiliated with or endorsed by SLF.

## Status

Progress is tracked in the
[implementation plan](docs/plan/implementation-plan.md); the behavior is defined
in the [specification](docs/spec/specification.md).

## Data license

The SLF data is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Products that display
it must visibly name the WSL Institute for Snow and Avalanche Research SLF, in
digital products as a link to [www.slf.ch](https://www.slf.ch).

## License

The code is licensed under the [MIT License](LICENSE).
