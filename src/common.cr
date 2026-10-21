# Generated from microsoft/fluentui-system-icons (MIT). Do not edit manually.
# Upstream commit: 4c94ad5f4081168c0d45bdc368f230ecb757cd09
# Source archive SHA-256: 08ae591157365d88b28a966032ef4d0c47e6cc1704479673d410c2e01bd62704
require "base64"
require "crimage"

module Icon
  module Fluent
    # Shared CrImage images. Copy before modifying.
    private def self.decode_png(encoded : String)
      CrImage.read(IO::Memory.new(Base64.decode(encoded)))
    end
  end
end
