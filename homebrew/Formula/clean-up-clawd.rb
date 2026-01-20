class CleanUpClawd < Formula
  desc "A beautiful terminal-based application for cleaning up directories"
  # TODO: Replace with your actual repository URL
  homepage "https://github.com/sahil/clean-up-clawd"
  
  # TODO: Replace with the actual URL to your release file
  # Example: https://github.com/sahil/clean-up-clawd/releases/download/v1.0.0/clean-up-clawd-v1.0.0-macos.tar.gz
  url "https://github.com/SahilFruitwala/clean-up-clawd/releases/download/v1.0.0/clean-up-clawd-v1.0.0-macos.tar.gz"
  
  # TODO: Replace with the SHA256 output from homebrew/build_release.sh
  sha256 "b9f74b9afea9f7c97098c0975ddcbad1179e39f7710fb12b19cefbfce2771e83"
  
  version "1.0.0"

  def install
    bin.install "clean-up-clawd"
  end

  test do
    # Since it's a TUI, we can't really test interactive mode, 
    # but we can check if the binary loads (if --help wasn't consumed by Textual/Click)
    # or just check if it exists. Textual apps often don't have --help by default unless configured.
    assert_predicate bin/"clean-up-clawd", :exist?
  end
end
