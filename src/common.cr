require "base64"
require "crimage"

module Icon
  module Fluent
    # Shared CrImage images. Copy before modifying.
    private def self.decode_png(encoded : String)
      CrImage.read(IO::Memory.new(Base64.decode(encoded)))
    end

    macro load_icons(group)
      {% for line in read_file("#{__DIR__}/data/#{group.id}.tsv").lines %}
        {% fields = line.strip.split("\t") %}
        {{ fields[0].id }} = decode_png({{ fields[1] }})
      {% end %}
    end
  end
end
