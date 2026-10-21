require "spec"
require "../src/20_regular"
require "../src/20_filled"
require "../src/32_light"
require "../src/24_color"
require "../src/16_filled"

describe Icon::Fluent do
  it "provides regular, filled, and light icons at their filename sizes" do
    Icon::Fluent::Add20Regular.bounds.width.should eq(20)
    Icon::Fluent::Add20Regular.bounds.height.should eq(20)
    Icon::Fluent::Add20Filled.bounds.width.should eq(20)
    Icon::Fluent::Add32Light.bounds.width.should eq(32)
    Icon::Fluent::Add32Light.bounds.height.should eq(32)
    Icon::Fluent::CommentEdit16Filled.bounds.width.should eq(16)
    Icon::Fluent::CommentEdit16Filled.bounds.height.should eq(16)
  end

  it "preserves transparent backgrounds and source colors" do
    image = Icon::Fluent::Alert24Color
    image.bounds.width.should eq(24)
    image.bounds.height.should eq(24)
    image.at(0, 0).rgba[3].should eq(0)
    red, green, blue, alpha = image.at(10, 2).rgba
    alpha.should be > 0
    red.should be > blue
    green.should be > blue
  end

  it "exposes language and direction variants" do
    Icon::Fluent::LocalLanguage20RegularJa.bounds.width.should eq(20)
    Icon::Fluent::Multiselect20FilledRtl.bounds.width.should eq(20)
  end
end
