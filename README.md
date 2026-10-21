# icon-fluent

[Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons) as pre-rendered `CrImage` constants for Crystal. Icons are square at the size in each SVG filename.

```yaml
dependencies:
  icon-fluent:
    github: kojix2/icon-fluent
```

```crystal
require "icon-fluent"

add = Icon::Fluent::Add20Filled
```

The shard includes every SVG from the pinned source archive: `regular`, `filled`, `light`, and `color`, including language and direction variants. Names follow the source SVG name, size, and style. For example, `Icon::Fluent::LocalLanguage20RegularJa` and `Icon::Fluent::Multiselect20FilledRtl`. Use `require "icon-fluent"` to load all variants, or `require "icon-fluent/20_filled"` to load one size and style. For 11 upstream SVGs whose dimensions differ from the size in their filenames, rendering uses the filename size for both width and height.

Constants are shared, mutable images. Copy an icon before editing it. Color icons retain their source colors and transparency.

## Regenerate

Maintainers need Python 3, librsvg, Cairo, and the source ZIP for commit `4c94ad5f4081168c0d45bdc368f230ecb757cd09` from [the upstream repository](https://github.com/microsoft/fluentui-system-icons/archive/4c94ad5f4081168c0d45bdc368f230ecb757cd09.zip).

```bash
python3 scripts/generate.py /path/to/fluentui-system-icons.zip
python3 scripts/generate.py /path/to/fluentui-system-icons.zip --check
```

The generator verifies the archive's SHA-256 before rendering. This shard is MIT licensed under [LICENSE](LICENSE). The bundled icons retain the upstream [LICENSE.fluent](LICENSE.fluent) and [NOTICE.fluent](NOTICE.fluent).
