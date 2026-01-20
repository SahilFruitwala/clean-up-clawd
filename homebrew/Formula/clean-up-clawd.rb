class CleanUpClawd < Formula
  desc "A beautiful terminal-based application for cleaning up directories"
  # TODO: Replace with your actual repository URL
  homepage "https://github.com/sahil/clean-up-clawd"
  
  # TODO: Replace with the actual URL to your release file
  # Example: https://github.com/sahil/clean-up-clawd/releases/download/v1.0.0/clean-up-clawd-v1.0.0-macos.tar.gz
  url "https://github.com/SahilFruitwala/clean-up-clawd/releases/download/v1.0.1/clean-up-clawd-v1.0.1-macos.tar.gz"
  
  # TODO: Replace with the SHA256 output from homebrew/build_release.sh
  sha256 "bb9b6db2f072b934f46568195e7d59a42fe0ac6dc458acfe520066c63a39dfdb"
  
  version "1.0.1"

  def install
    # Install the entire directory to libexec
    libexec.install Dir["*"]
    
    # Symlink the binary to bin
    bin.install_symlink libexec/"clean-up-clawd"
  end

  test do
    # Since it's a TUI, we can't really test interactive mode, 
    # but we can check if the binary loads (if --help wasn't consumed by Textual/Click)
    # or just check if it exists. Textual apps often don't have --help by default unless configured.
    assert_predicate bin/"clean-up-clawd", :exist?
  end
end
