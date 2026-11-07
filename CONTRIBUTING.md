# Contributing

## Adding a result to a task pack

Build the profile the pack names, run its `eval.md` protocol, and append a row to the `eval.results` list in `taskpack.yaml` with your robot name, the date and your success count. Open a pull request with that change and a photo of your setup in the pull request description.

## Adding a tool, fixture or camera mount

Put it under `hardware/<kind>/<name>_v<N>/` with the STL files, the source CAD if you have it, and a `README.md` stating what it fits, print settings, and its measurements (for a tool: opening width, jaw depth, padding).

## Adding a task pack

Copy `taskpacks/laundry-sort/` and follow `docs/interface-spec.md` section 7. A pack is accepted once it has at least one passing result.

## Changing the interface spec

Open an issue first. Minor changes add things; anything that breaks fit, wiring or observation keys is a major version and needs a migration note in the spec.
