jQuery TinyTimer Plugin
=======================

TinyTimer is a very simple jQuery plugin that lets you create a countdown (or
countup) timer on a web page.

Basic Usage
-----------

Create a HTML element for your timer somewhere in the page:

```html
<p>
	Time remaining: <span id="timer"></span>
</p>
```

Then, wrap that element in a jQuery object and call its `tinyTimer` method,
passing the date to count to as the `to` option. Here's an example that starts a
30-minute countdown:

```javascript
var d = new Date();
d.setMinutes(d.getMinutes() + 30);
$('#timer').tinyTimer({ to: d });
```

To create a timer counting up from a moment in time, use the `from` option
instead of `to`. This produces a timer that shows the number of days since a
specific date:

```javascript
var d = new Date('January 1, 2013');
$('#timer').tinyTimer({ from: d, format: '%d' });
```

Options
-------

- `format`

  The format used to display the date/time. See [Time Format](#time-format) for
  details.

- `from`

  Date/time to count (up) from. Can be a JavaScript Date object or a string
  ([IETF-compliant RFC 2822
  timestamp](http://tools.ietf.org/html/rfc2822#page-14)).

- `to`

  Date/time to count (down) to.

- `onTick`

  Callback function to be invoked on every tick (every second). See
  [Callback Functions](#callback-functions) for details.

- `onEnd`

  Callback function to be invoked when the countdown is over. See
  [Callback Functions](#callback-functions) for details.

<a id="time-format"></a>
Time Format
-----------

The `format` option allows you to define how the time will be displayed. The
different values are represented by tokens composed of a percent sign and a
formatting character:

- `%d` - days
- `%h` - hours
- `%m` - minutes
- `%s` - seconds

If the format character is preceded by `0` (e.g., `%0m`), then single-digit
numbers will be displayed with a leading zero (e.g., `04:20` instead of `4:20`).
If it is preceded by `-` (e.g., `%-h`), then the value won't be displayed at all
if its value is zero. The two modifiers can be combined (e.g., `%-0h`).

The above format characters can also be used in uppercase form, in which case
they represent _total_ quantities. For instance, if the current time is 2 days
and 4 hours, `d` and `h` would be 2 and 4 respectively, while the values of `D`
and `H` would be 2 and 52 (2 * 24 + 4 = 52).

The format character can also be followed by a suffix, enclosed in curly braces,
to denote the unit of time. You can set different suffixes for singular and
plural form by separating them with `|`. For example, a format setting of `%d
{day|days}` would output the number of days followed by the appropriate form.

Anything else in the format string will be included in the output as it is.

A few examples:
- `%-d {day,|days,} %0h {hour|hours}` - 2 days, 07 hours
- `%m minutes and %s seconds` - 12 minutes and 4 seconds
- `%H:%0m:%0s` - 55:12:04

The default format is `%-H{:}%0m:%0s`, which is the total number of hours (not
displayed if zero), then minutes and seconds, separated by colons.

<a id="callback-functions"></a>
Callback Functions
------------------

The `onTick` and `onEnd` callback functions take one argument, which is an
object that represents the current value of the timer. This object has the
following properties:

- `s` - seconds
- `m` - minutes
- `h` - hours
- `d` - days
- `S` - total seconds
- `M` - total minutes
- `H` - total hours
- `D` - total days (same as `d`)
- `text` - textual representation of the current time (formatted according to
  the `format` option)

Here's an example of a timer that counts from the time that the page is loaded
and uses the `onTick` callback function to display an alert every minute:

```javascript
$('#timer').tinyTimer({
	from: Date.now(),
	onTick: function (val) {
		if (val.m > 0 && val.s == 0)
			alert('You decided to stay on this site for another minute! Yay!');
	}
});
```

Using with Moment.js
--------------------

TinyTimer can be used with the great [Moment.js](http://momentjs.com/) library,
which makes date manipulation much easier than with plain Date objects. You just
need to convert the moment object to `Date` using its `toDate` method before
passing it as `to` or `from`:

```javascript
// 30-minute countdown
var m = moment().add('minutes', 30);
$('#timer').tinyTimer({ to: m.toDate() });

// Hours since the beginning of the week
var m = moment().startOf('week');
$('#timer').tinyTimer({ from: m.toDate(), format: '%H' });
```
