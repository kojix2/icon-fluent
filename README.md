# icon-fluent

[Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons) as pre-rendered `CrImage` constants for Crystal. Images use the size in each SVG filename.

```yaml
dependencies:
  icon-fluent:
    github: kojix2/icon-fluent
```

```crystal
require "icon-fluent"

icon = Icon::Fluent::Add20Filled
```

Includes every upstream SVG: `regular`, `filled`, `light`, and `color`, including language and direction variants. Names follow the SVG filenames, size, and style. Use `require "icon-fluent/20_filled"` to load one size and style. Constants are shared, mutable images; copy before editing. Source colors and transparency are retained.

## Regenerate

Requires Python 3, librsvg, Cairo, and a ZIP of the upstream repository.

```bash
python3 scripts/generate.py /path/to/fluentui-system-icons.zip
python3 scripts/generate.py /path/to/fluentui-system-icons.zip --check
```

MIT: [shard](LICENSE), [upstream icons](LICENSE.fluent) and [notice](NOTICE.fluent).
