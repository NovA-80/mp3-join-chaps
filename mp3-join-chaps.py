#!/usr/bin/env python3
# encoding: utf-8
#
# Joins several mp3 files into a single one and embeds original time stamps
# as chapter marks in the format of ID3v2.4 Chapters specification.
#
# It is assumed that input mp3 files are listed in a desired order,
# and each input file name acts as the chapter title (without .mp3 suffix).
#
# The ID3 tags in the joined mp3 file are copied from the first input file
# and extended by chapters info.
#
# For mp3 joining the `ffmpeg` tool is called that should be available
# in the PATH or the appropriate constant below can be adjusted.
#
# Author: Andrey Novikov, 2023-07-03


import eyed3
import argparse
from pathlib import Path
import subprocess


# FFMPEG binary name
FFMPEG = 'ffmpeg'


def main():
    #
    # Parse command arguments
    #
    parser = argparse.ArgumentParser(
        description="Joins mp3 files AND embeds ID3 chapter marks")
    parser.add_argument('ifiles', metavar="IN.mp3", nargs='+',
                        help="input mp3 files")
    parser.add_argument('-o', metavar="OUT.mp3", default="joined.mp3",
                        help="output mp3 file name (default: `%(default)s`)")
    parser.add_argument('-e', metavar='FMT', default='timecodes',
                        nargs='?', const='timecodes',
                        choices=['timecodes', 'cue', 'all'],
                        help="Export chapters to OUT(.chapters.txt|.cue) "
                             "according to FMT=(timecodes|cue|all)")
    args = parser.parse_args()

    # ---

    #
    # Make chapter marks from input file names & lengths
    #
    chaps = []  # [ ((tstart, tend), title), ... ]
    t0 = 0.0    # timestamp in milliseconds
    for fn in args.ifiles:
        f = eyed3.load(fn)
        title = Path(fn).stem
        t1 = t0 + f.info.time_secs * 1000.0
        chaps.append(((t0, t1), title))
        t0 = t1
        del f

    # print(chaps)

    # ---

    print(f"\n* Joining input MP3 files into `{args.o}`")

    subprocess.run([FFMPEG, '-hide_banner', '-loglevel','error', '-stats',
                   '-i', 'concat:' + '|'.join(args.ifiles),
                   '-c', 'copy',
                   args.o], check=True)

    # ---

    print(f"\n* Embedding chapter marks to `{args.o}`")

    ofile = eyed3.load(args.o)
    _child_ids = []
    for i, (times, title) in enumerate(chaps):
        element_id = f"ch{i}".encode()
        ofile.tag.chapters.set(element_id, times)
        ofile.tag.chapters[element_id].title = title
        _child_ids.append(element_id)

    ofile.tag.table_of_contents.set(b"toc", toplevel=True, child_ids=_child_ids,
                                    description="Table of Contents")

    ofile.tag.save()

    # ---

    print(f"\n* Exporting chapter marks")

    fmts = ()
    if args.e == 'all':
        fmts = ('timecodes', 'cue')
    else:
        fmts = (args.e,)

    for fmt in fmts:
        fn = Path(args.o).with_suffix('.cue' if fmt=='cue' else '.chapters.txt')

        print("  ->", fn)
        with open(fn, "w") as f:
            if fmt == 'cue':
                f.write(f'FILE "{Path(args.o).name}" MP3\n')
            for i, (times, title) in enumerate(chaps):
                if fmt == "cue":
                    f.write(f"TRACK {i+1:02d} AUDIO\n")
                    f.write(f'    TITLE "{title}"\n')
                    f.write(f"    INDEX 01 {to_cuesheet(times[0])}\n")
                else:
                    f.write(f"{to_timecode(times[0])} {title}\n")

    # ---
#


def to_timecode(ms):
    """from milliseconds to timecode """
    ss = int(ms / 1000.0)
    nn = int(ms - (ss * 1000))
    mm = int(ss / 60.0)
    ss -= (mm * 60)
    hh = int(mm / 60.0)
    mm -= (hh * 60)

    return f"{hh:02d}:{mm:02d}:{ss:02d}.{nn:03d}"


def to_cuesheet(ms):
    """from milliseconds to cuesheet track"""
    ss, nn = divmod(int(ms), 1000)
    mm, ss = divmod(ss, 60)
    fr = round(int(nn) * 0.075)

    return f"{mm:02d}:{ss:02d}:{fr:02d}"


if __name__ == '__main__':
    main()
