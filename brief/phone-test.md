# Real phone test (5 minutes)

## Open it on the phone
1. The phone and this computer must be on the **same Wi-Fi**.
2. On the computer run `open-page.bat` (it must be running the whole test).
3. On the phone, open Chrome (Android) or Safari (iPhone) and type: `http://192.168.1.2:8000/?perf`
   (If the address does not work, the computer's address changed: run `ipconfig` and use the "IPv4 Address" of the Wi-Fi or Ethernet connection. If Windows asks to allow Python through the firewall, choose Allow on private networks.)
4. The small green box at the top left shows fps (frames per second). Do not use `?still`; that switch is only for desktop checking.

## Try these, and note what you see
| # | Do this | Good looks like | Write down |
|---|---|---|---|
| 1 | Open the page and wait | The candle appears dark, then lights. No white flash, no blank screen | seconds until the candle shows |
| 2 | Scroll slowly from top to About | Candle turns, then burns down; no stutter | fps (green box) in the hero and in About |
| 3 | Reach the shelf; swipe sideways | The lit flame moves candle to candle; the swipe snaps | fps while swiping, any lag |
| 4 | Tap the lit candle, then the "التفاصيل" button | Panel slides up from the bottom, the photo and text are readable, the order button stays at the bottom | anything cut off or hard to tap |
| 5 | Tap "اطلب عبر واتساب" | WhatsApp opens with the candle's name in the message | the number is still 0000000000 (placeholder) |
| 6 | Read the About title and steps | Title in 2 lines, steps lit one by one | any lone words or overlaps |
| 7 | Leave it open for 3 minutes | The phone does not get hot; battery drops only a little | battery % before and after, warm or not |
| 8 | Turn the phone sideways and back | Layout redraws, no blank canvas | anything broken |

## Numbers to send back
- Phone model and browser
- fps in the hero / About / shelf (30 or more is fine; under 20 is a problem)
- "slowest frame" (under 100 ms is fine)
- Battery used in 3 minutes, and whether it got warm
- Any screenshot of something that looks wrong
