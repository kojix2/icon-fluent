#!/usr/bin/env python3
"""Generate Crystal CrImage constants from the pinned Fluent UI icon archive."""

import argparse
import base64
import ctypes as c
from ctypes.util import find_library
import hashlib
from pathlib import Path
import re
import zipfile


SOURCE_COMMIT = "4c94ad5f4081168c0d45bdc368f230ecb757cd09"
SOURCE_SHA256 = "08ae591157365d88b28a966032ef4d0c47e6cc1704479673d410c2e01bd62704"
SOURCE_URL = f"https://github.com/microsoft/fluentui-system-icons/archive/{SOURCE_COMMIT}.zip"
SVG = re.compile(
    r"[^/]+/assets/[^/]+/(?:(?P<locale>[^/]+)/)?SVG/"
    r"ic_fluent_(?P<name>[a-z0-9_]+)_(?P<size>\d+)_"
    r"(?P<style>regular|filled|light|color)(?:_(?P<direction>ltr|rtl))?\.svg\Z"
)


def bind(library, name, result, *args):
    function = getattr(c.CDLL(find_library(library) or library), name)
    function.restype, function.argtypes = result, args
    return function


ptr, integer = c.c_void_p, c.c_int
new_handle = bind("rsvg-2", "rsvg_handle_new_from_data", ptr, c.c_char_p, c.c_size_t, ptr)
render_document = bind("rsvg-2", "rsvg_handle_render_document", integer, ptr, ptr, ptr, ptr)
new_surface = bind("cairo", "cairo_image_surface_create", ptr, integer, integer, integer)
new_context = bind("cairo", "cairo_create", ptr, ptr)
write_png_stream = bind("cairo", "cairo_surface_write_to_png_stream", integer, ptr, ptr, ptr)
destroy_context = bind("cairo", "cairo_destroy", None, ptr)
destroy_surface = bind("cairo", "cairo_surface_destroy", None, ptr)
unref = bind("gobject-2.0", "g_object_unref", None, ptr)


class Rectangle(c.Structure):
    _fields_ = [(field, c.c_double) for field in ("x", "y", "width", "height")]


WRITE_CALLBACK = c.CFUNCTYPE(integer, ptr, ptr, c.c_uint)


def rasterize(svg, name, size):
    handle = new_handle(svg, len(svg), None)
    if not handle:
        raise ValueError(f"Cannot parse SVG: {name}")
    surface = new_surface(0, size, size)  # CAIRO_FORMAT_ARGB32
    context = new_context(surface)
    png = bytearray()

    @WRITE_CALLBACK
    def collect(_closure, data, length):
        png.extend(c.string_at(data, length))
        return 0  # CAIRO_STATUS_SUCCESS

    try:
        viewport = Rectangle(0, 0, size, size)
        if not render_document(handle, context, c.byref(viewport), None):
            raise ValueError(f"Cannot render SVG: {name}")
        if write_png_stream(surface, collect, None):
            raise ValueError(f"Cannot encode PNG: {name}")
        result = bytes(png)
        if (result[:8] != b"\x89PNG\r\n\x1a\n" or
                result[16:24] != size.to_bytes(4, "big") * 2):
            raise ValueError(f"Invalid PNG dimensions: {name}")
        return result
    finally:
        destroy_context(context)
        destroy_surface(surface)
        unref(handle)


def pascal(value):
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def collect_icons(archive):
    icons = []
    identifiers = {}
    with zipfile.ZipFile(archive) as source:
        for path in source.namelist():
            if "/assets/" not in path or "/SVG/" not in path or not path.endswith(".svg"):
                continue
            match = SVG.fullmatch(path)
            if not match:
                raise ValueError(f"Unexpected Fluent SVG path: {path}")
            parts = match.groupdict()
            size = int(parts["size"])
            if size <= 0:
                raise ValueError(f"Invalid icon size: {path}")
            identifier = pascal(parts["name"]) + parts["size"] + pascal(parts["style"])
            if parts["locale"]:
                identifier += pascal(parts["locale"])
            if parts["direction"]:
                identifier += pascal(parts["direction"])
            if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", identifier):
                raise ValueError(f"Invalid Crystal identifier: {identifier} ({path})")
            if identifier in identifiers:
                raise ValueError(f"Conflicting Crystal identifier: {identifier}: {identifiers[identifier]}, {path}")
            identifiers[identifier] = path
            icons.append((size, parts["style"], identifier, path))
        if not icons:
            raise ValueError("No Fluent SVG icons found in source archive")
        icons.sort(key=lambda item: (item[0], item[1], item[2]))
        return [(size, style, identifier, path, source.read(path))
                for size, style, identifier, path in icons]


def generated_files(archive):
    icons = collect_icons(archive)
    groups = {}
    for size, style, identifier, path, svg in icons:
        key = f"{size}_{style}"
        groups.setdefault(key, []).append((size, identifier, path, svg))

    header = ("# Generated from microsoft/fluentui-system-icons (MIT). Do not edit manually.\n"
              f"# Upstream commit: {SOURCE_COMMIT}\n"
              f"# Source archive SHA-256: {SOURCE_SHA256}\n")
    common = (header + 'require "base64"\nrequire "crimage"\n\n'
              'module Icon\n  module Fluent\n'
              '    # Shared CrImage images. Copy before modifying.\n'
              '    private def self.decode_png(encoded : String)\n'
              '      CrImage.read(IO::Memory.new(Base64.decode(encoded)))\n'
              '    end\n  end\nend\n')
    results = {Path("common.cr"): common}
    for key, entries in sorted(groups.items()):
        lines = [header.rstrip(), 'require "./common"', '', 'module Icon', '  module Fluent']
        for size, identifier, path, svg in entries:
            png = rasterize(svg, path, size)
            lines.append(f"    # {path.split('/assets/', 1)[1]} ({size}x{size})")
            lines.append(f'    {identifier} = decode_png("{base64.b64encode(png).decode()}")')
        lines += ['  end', 'end', '']
        results[Path(f"{key}.cr")] = "\n".join(lines)
        print(f"Rendered {key}: {len(entries)} icons", flush=True)
    results[Path("icon-fluent.cr")] = header + "".join(
        f'require "./{key}"\n' for key in sorted(groups))
    return results, len(icons)


def generate(archive, output_dir, check=False):
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Source archive SHA-256 mismatch: {digest}; expected {SOURCE_SHA256}")
    results, count = generated_files(archive)
    existing = {path.relative_to(output_dir) for path in output_dir.glob("[0-9]*_*.cr")}
    expected = {path for path in results if path.name[0].isdigit()}
    stale = existing - expected
    if (output_dir / "fluent.cr").is_file():
        stale.add(Path("fluent.cr"))
    root_dir = output_dir.parent
    stale_wrappers = {path.relative_to(root_dir) for path in root_dir.glob("[0-9]*_*.cr")}
    if (root_dir / "fluent.cr").is_file():
        stale_wrappers.add(Path("fluent.cr"))
    if check:
        mismatched = [str(path) for path, content in results.items()
                      if not (output_dir / path).is_file() or (output_dir / path).read_text() != content]
        if mismatched or stale or stale_wrappers:
            raise ValueError(f"Generated files differ: {mismatched}; stale files: {sorted(map(str, stale | stale_wrappers))}")
        print(f"OK: {count} icons, generated files match")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        for path in stale:
            (output_dir / path).unlink()
        for path in stale_wrappers:
            (root_dir / path).unlink()
        for path, content in results.items():
            (output_dir / path).write_text(content)
        print(f"Generated {count} icons in {len(results)} source files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help=f"Source ZIP from {SOURCE_URL}")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "src")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(args.archive, args.output_dir, args.check)
