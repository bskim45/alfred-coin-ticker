<h1 align="center">
  <a href="https://github.com/bskim45/alfred-coin-ticker" title="Coin Ticker for Alfred Workflow">
    <img alt="icon" src="https://raw.githubusercontent.com/bskim45/alfred-coin-ticker/main/icon.png" width="128px" />
  </a>
  <br />
  Coin Ticker for Alfred Workflow
</h1>

An [Alfred Workflow](http://www.alfredapp.com/) that provides the current price
and status about cryptocurrency from [cryptocompare.com].

Supports Alfred 4 on macOS 12.3+ (Python 3.8+).

## ⚠️ Using this workflow on macOS 12.3+ Monterey
[2.0.0](https://github.com/bskim45/alfred-coin-ticker/releases/tag/2.0.0)
is the first version that supports macOS 12.3+ (Python 3.8+).
Please upgrade your workflow version to 2.0.0 or later
if you are using macOS 12.3+.

Feel free to open issues for any troubles regarding this change.

## ⚠️ Note to macOS 12.2 or below users
[1.1.0](https://github.com/bskim45/alfred-coin-ticker/releases/tag/1.1.0)
is the last version that supports macOS 12.2 and below (Python 2).
Please do not upgrade to 2.x version if you are using macOS 12.2 or below.

## Install

[Download the latest package][latest release]

## Usage

Simply type `coin` to get the current price of favorite coins.

<div style="text-align:center">
  <img src="docs/screenshot_coin.png" width="512px" alt="workflow screenshot">
</div>

`coin list` shows the current price of the top 10 coins by market cap.

- Press `Enter ⏎` to open associated `coinmarketcap.com` website.
- Press `⌘ ⏎` to copy the current price to the clipboard.
- Press `⌥ ⏎` to copy current ticker (ex. `BTC`) to the clipboard.

`coin [TICKER]` shows the current price of the coin with that ticker.

`coin add [TICKER] [POSITION(optional)]` adds new coin to the favorites.
Position starts from 1.

`coin remove [TICKER]` removes a coin from the favorites.

`coin set currency [CURRENCY]` sets the fiat currency (3 letters).

`coin reset` resets all settings to default and deletes all caches/saved data.
Please use with caution.

`coin help` shows all available commands.

## Artworks

- All cryptocurrency icons are from [cryptocompare.com]
- App icon https://www.iconfinder.com/icons/2907507/bitcoin_btc_coin_cryptocurrency_icon

## License

The code is released under the MIT license. See [LICENSE](LICENSE) for details.

Awesome [alfred-workflow](https://github.com/NorthIsUp/alfred-workflow-py3)
library by [@NorthIsUp](https://github.com/NorthIsUp) is also released under
[MIT License](alfred-workflow/LICENCE.txt).

[alfred-workflow](https://github.com/NorthIsUp/alfred-workflow) is
originally created by [@deanishe](https://github.com/deanishe)
and ported to Python 3 by  [@NorthIsUp](https://github.com/NorthIsUp).

[cryptocompare.com]: https://www.cryptocompare.com/
[latest release]: https://github.com/bskim45/alfred-coin-ticker/releases/latest/download/alfred-coin-ticker.alfredworkflow
