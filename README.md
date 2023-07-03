# mp3-join-chaps

Command line tool to join several mp3 files into a single one and to embed input file lengths as chapter markers.
This can be used to bind several parts of a podcast or audiobook into a single file and still provide the table
of original contents. The time markers are embedded in the format of ID3v2.4 Chapters specification that is supported
by many audio players. The tool is inspired by [mp3chapters](https://github.com/rfjaquez/mp3chapters) and extends that
with files joining functionality.

## Requirements

- `ffmpeg` binary executable to join mp3 files. This should be available in the PATH or the appropriate constant in the
   head of the source can be adjusted
- [eyeD3](https://github.com/nicfit/eyeD3) lib to write chapters details
- Python 3.6+ to glue everithing

## Usage

If you have a directory `abook` with files named like `01.mp3` .. `42.mp3`, then the call
```
$ ./mp3-join-chaps.py  abook/*.mp3
```
will create in the current directory the file `joined.mp3` with the embedded chapter markers
entitled as '01', '02', ..., '42'. The ID3 tags in the joined mp3 file are copied from
the first input file and extended by the chapters info. These tags can be edited afterwards
by any tag editing software, but that should keep ID3v2.4 tags.

## Advanced usage

The full command line template is
```
mp3-join-chaps.py [-h] [-o OUT.mp3] [-e [FMT]]  IN1.mp3 IN2.mp3 [...]
```
Here,
- positional arguments
  - `IN1.mp3`, `IN2.mp3`, `...` input mp3 files to be joined that **MUST** be listed
    in a desired order.  Each file name acts as the chapter title (without .mp3 suffix).
    Metainfo (ID3 tags) from the first file is copied as is into the resulting file.
- optional arguments:
  - `-h`, `--help` show usage info and exits
  - `-o OUT.mp3` output resulting mp3 file name (default: `joined.mp3`)
  - `-e [FMT]` additionally export chapter marks to `OUT.chapters.txt` and/or `OUT.cue` file(s)
    according to the format FMT = timecodes|cue|all (default: 'timecodes'). This can be used to
    rename chapters and re-embed them using e.g. [mp3chapters](https://github.com/rfjaquez/mp3chapters)
